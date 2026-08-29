import httpx
import pytest

from dashboard.backend_client import BackendClient, BackendClientError


def transport(handler):
    return httpx.MockTransport(handler)


def test_client_session_case_events_transcript_handoff_and_command():
    calls = []

    def handler(request):
        calls.append((request.method, request.url.path, request.url.params))
        path = request.url.path
        if path == "/api/v1/sessions" and request.method == "POST":
            return httpx.Response(201, json={"session_id": "ses_1", "case_id": "case_1"})
        if path.endswith("/case"):
            return httpx.Response(200, json={"case_id": "case_1", "revision": 0})
        if path.endswith("/events"):
            return httpx.Response(200, json={"events": [{"sequence": 1}]})
        if path.endswith("/transcript"):
            return httpx.Response(200, json={"turns": []})
        if path.endswith("/handoff"):
            return httpx.Response(200, json={"state": "not_requested"})
        if path.endswith("/commands"):
            return httpx.Response(200, json={"accepted": True, "case_revision": 1})
        return httpx.Response(404)

    client = BackendClient(transport=transport(handler))
    assert client.create_session()["session_id"] == "ses_1"
    assert client.get_case("ses_1")["revision"] == 0
    assert client.get_events("ses_1", 0)[0]["sequence"] == 1
    assert client.get_transcript("ses_1") == []
    assert client.get_handoff("ses_1")["state"] == "not_requested"
    assert client.send_command("ses_1", "request_handoff", 0)["accepted"] is True
    assert len(calls) == 6


def test_client_reports_connection_failure():
    def handler(request):
        raise httpx.ConnectError("offline", request=request)

    with pytest.raises(BackendClientError, match="Cannot reach"):
        BackendClient(transport=transport(handler)).health()


def test_snapshot_recovery_fetches_case_and_complete_events():
    def handler(request):
        if request.url.path.endswith("/case"):
            return httpx.Response(200, json={"revision": 4})
        return httpx.Response(200, json={"events": [{"sequence": 1}, {"sequence": 2}]})

    snapshot, events = BackendClient(transport=transport(handler)).recover_snapshot("ses_1")
    assert snapshot["revision"] == 4
    assert [event["sequence"] for event in events] == [1, 2]
