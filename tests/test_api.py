from fastapi.testclient import TestClient

from backend.main import app


def create(client: TestClient):
    response = client.post("/api/v1/sessions", json={"caller": {"phone_masked": "+91-XXXXX"}, "locale_hints": ["hi-IN"]})
    assert response.status_code == 201
    return response.json()


def test_health_ready_and_session_snapshot():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert client.get("/ready").json()["capabilities"]["agora"] is False
        session = create(client)
        snapshot = client.get(f"/api/v1/sessions/{session['session_id']}/case")
        assert snapshot.status_code == 200
        assert snapshot.json()["revision"] == 0


def test_create_session_idempotency():
    with TestClient(app) as client:
        headers = {"Idempotency-Key": "same-create"}
        first = client.post("/api/v1/sessions", json={}, headers=headers)
        second = client.post("/api/v1/sessions", json={}, headers=headers)
        assert first.json() == second.json()


def test_handoff_commands_revision_and_idempotency():
    with TestClient(app) as client:
        session = create(client)
        sid = session["session_id"]
        command = {"command_id": "cmd-1", "type": "request_handoff", "expected_revision": 0,
                   "payload": {"reason_code": "operator_requested"}}
        first = client.post(f"/api/v1/sessions/{sid}/commands", json=command)
        assert first.status_code == 200
        assert first.json()["case_revision"] == 1
        event_types = [event["type"] for event in client.get(f"/api/v1/sessions/{sid}/events").json()["events"]]
        assert event_types[-2:] == ["handoff.requested", "case.updated"]
        duplicate = client.post(f"/api/v1/sessions/{sid}/commands", json=command)
        assert duplicate.json()["duplicate"] is True
        stale = client.post(f"/api/v1/sessions/{sid}/commands", json={**command, "command_id": "cmd-2"})
        assert stale.status_code == 409


def test_event_backlog_and_websocket():
    with TestClient(app) as client:
        session = create(client)
        sid = session["session_id"]
        events = client.get(f"/api/v1/sessions/{sid}/events").json()["events"]
        assert [event["sequence"] for event in events] == [1]
        with client.websocket_connect(f"/api/v1/sessions/{sid}/ws?after_sequence=0") as websocket:
            event = websocket.receive_json()
            assert event["type"] == "session.created"


def test_unimplemented_agora_endpoint_is_explicit():
    with TestClient(app) as client:
        sid = create(client)["session_id"]
        response = client.post(f"/api/v1/sessions/{sid}/agent:start")
        assert response.status_code == 501
        assert response.json()["error"]["code"] == "NOT_IMPLEMENTED"
