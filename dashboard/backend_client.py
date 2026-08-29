from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

import httpx


DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"


class BackendClientError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, code: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class BackendClient:
    def __init__(self, base_url: str | None = None, timeout: float = 3.0,
                 transport: httpx.BaseTransport | None = None):
        self.base_url = (base_url or os.getenv("ECHOSPHERE_BACKEND_URL", DEFAULT_BACKEND_URL)).rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout, transport=transport)

    def close(self) -> None:
        self._client.close()

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            try:
                detail = exc.response.json().get("error", {})
            except ValueError:
                detail = {}
            raise BackendClientError(
                detail.get("message", f"Backend returned HTTP {exc.response.status_code}"),
                status_code=exc.response.status_code,
                code=detail.get("code"),
            ) from exc
        except (httpx.RequestError, ValueError) as exc:
            raise BackendClientError(f"Cannot reach or decode the EchoSphere backend: {exc}") from exc

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def create_session(self, caller: dict[str, Any] | None = None,
                       locale_hints: list[str] | None = None) -> dict[str, Any]:
        return self._request(
            "POST", "/api/v1/sessions",
            headers={"Idempotency-Key": f"dashboard-{uuid4().hex}"},
            json={"caller": caller or {}, "locale_hints": locale_hints or [],
                  "client": {"type": "streamlit_web"}},
        )

    def get_case(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/sessions/{session_id}/case")

    def get_events(self, session_id: str, after_sequence: int = 0) -> list[dict[str, Any]]:
        data = self._request("GET", f"/api/v1/sessions/{session_id}/events",
                             params={"after_sequence": after_sequence})
        return data["events"]

    def get_transcript(self, session_id: str) -> list[dict[str, Any]]:
        return self._request("GET", f"/api/v1/sessions/{session_id}/transcript")["turns"]

    def get_handoff(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/sessions/{session_id}/handoff")

    def send_command(self, session_id: str, command_type: str, expected_revision: int,
                     payload: dict[str, Any] | None = None, command_id: str | None = None) -> dict[str, Any]:
        command_id = command_id or f"cmd_{uuid4().hex}"
        return self._request(
            "POST", f"/api/v1/sessions/{session_id}/commands",
            headers={"Idempotency-Key": command_id},
            json={"command_id": command_id, "type": command_type,
                  "expected_revision": expected_revision, "payload": payload or {}},
        )

    def recover_snapshot(self, session_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Fetch canonical state and complete event history after a detected gap."""
        return self.get_case(session_id), self.get_events(session_id, after_sequence=0)
