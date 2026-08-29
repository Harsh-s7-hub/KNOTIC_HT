from __future__ import annotations

from datetime import datetime
from typing import Any, MutableMapping

from dashboard.backend_client import BackendClient, BackendClientError


CONNECTED = "CONNECTED"
RECONNECTING = "RECONNECTING"
DISCONNECTED = "DISCONNECTED"


def initialize_live_state(state: MutableMapping[str, Any]) -> None:
    defaults = {
        "app_mode": "DEMO",
        "live_session_id": None,
        "live_case_snapshot": None,
        "live_events": [],
        "live_transcript": [],
        "live_handoff": None,
        "live_last_sequence": 0,
        "live_connection_status": DISCONNECTED,
        "live_error": None,
        "live_recovery_count": 0,
    }
    for key, value in defaults.items():
        if key not in state:
            state[key] = value


def start_live_session(state: MutableMapping[str, Any], client: BackendClient) -> None:
    state["live_connection_status"] = RECONNECTING
    try:
        created = client.create_session(locale_hints=["hi-IN", "en-IN"])
        state["live_session_id"] = created["session_id"]
        state["live_last_sequence"] = 0
        state["live_events"] = []
        refresh_live_state(state, client)
    except BackendClientError as exc:
        state["live_connection_status"] = DISCONNECTED
        state["live_error"] = str(exc)
        raise


def apply_events(state: MutableMapping[str, Any], events: list[dict[str, Any]],
                 client: BackendClient) -> bool:
    """Apply ordered events; recover canonical state when the stream has a gap."""
    session_id = state.get("live_session_id")
    last = int(state.get("live_last_sequence", 0))
    for event in sorted(events, key=lambda item: item["sequence"]):
        sequence = int(event["sequence"])
        if sequence <= last:
            continue
        if sequence != last + 1:
            snapshot, complete_events = client.recover_snapshot(session_id)
            state["live_case_snapshot"] = snapshot
            state["live_events"] = complete_events
            state["live_last_sequence"] = max((item["sequence"] for item in complete_events), default=0)
            state["live_recovery_count"] = int(state.get("live_recovery_count", 0)) + 1
            return True
        state["live_events"].append(event)
        last = sequence
        state["live_last_sequence"] = last
        if event["type"] == "case.updated" and event.get("payload", {}).get("snapshot"):
            state["live_case_snapshot"] = event["payload"]["snapshot"]
    return False


def refresh_live_state(state: MutableMapping[str, Any], client: BackendClient) -> None:
    session_id = state.get("live_session_id")
    if not session_id:
        return
    state["live_connection_status"] = RECONNECTING
    try:
        events = client.get_events(session_id, int(state.get("live_last_sequence", 0)))
        recovered = apply_events(state, events, client)
        if not recovered or state.get("live_case_snapshot") is None:
            state["live_case_snapshot"] = client.get_case(session_id)
        state["live_transcript"] = client.get_transcript(session_id)
        state["live_handoff"] = client.get_handoff(session_id)
        state["live_connection_status"] = CONNECTED
        state["live_error"] = None
    except BackendClientError as exc:
        state["live_connection_status"] = DISCONNECTED
        state["live_error"] = str(exc)
        raise


def send_live_command(state: MutableMapping[str, Any], client: BackendClient,
                      command_type: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    case = state.get("live_case_snapshot") or {}
    result = client.send_command(state["live_session_id"], command_type,
                                 int(case.get("revision", 0)), payload)
    refresh_live_state(state, client)
    return result


def live_timeline(state: MutableMapping[str, Any]) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    for event in state.get("live_events", []):
        occurred = event.get("occurred_at", "")
        try:
            time_text = datetime.fromisoformat(occurred.replace("Z", "+00:00")).strftime("%H:%M:%S")
        except (TypeError, ValueError):
            time_text = ""
        timeline.append({"type": "event", "text": event.get("type", "event"),
                         "icon": "⚡", "time": time_text})
    for turn in state.get("live_transcript", []):
        timeline.append({"type": "message", "role": turn.get("role", "caller"),
                         "text": turn.get("text", ""), "time": turn.get("time", ""),
                         "lang": turn.get("lang", "")})
    return timeline
