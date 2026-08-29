import pytest

from dashboard.backend_client import BackendClientError
from dashboard.live_state import CONNECTED, DISCONNECTED, apply_events, initialize_live_state, refresh_live_state, start_live_session


class FakeClient:
    def __init__(self):
        self.recoveries = 0

    def create_session(self, **kwargs):
        return {"session_id": "ses_1"}

    def get_events(self, session_id, after_sequence=0):
        return [{"sequence": 1, "type": "session.created", "payload": {}}] if after_sequence == 0 else []

    def get_case(self, session_id):
        return {"session_id": session_id, "case_id": "case_1", "revision": 0}

    def get_transcript(self, session_id):
        return []

    def get_handoff(self, session_id):
        return {"state": "not_requested"}

    def recover_snapshot(self, session_id):
        self.recoveries += 1
        return ({"session_id": session_id, "revision": 3},
                [{"sequence": 1}, {"sequence": 2}, {"sequence": 3}])


def test_start_session_loads_canonical_state_and_events():
    state = {}
    initialize_live_state(state)
    start_live_session(state, FakeClient())
    assert state["live_session_id"] == "ses_1"
    assert state["live_case_snapshot"]["case_id"] == "case_1"
    assert state["live_last_sequence"] == 1
    assert state["live_connection_status"] == CONNECTED


def test_sequence_gap_forces_snapshot_recovery():
    state = {"live_session_id": "ses_1", "live_last_sequence": 1,
             "live_events": [{"sequence": 1}], "live_recovery_count": 0}
    client = FakeClient()
    recovered = apply_events(state, [{"sequence": 3, "type": "case.updated", "payload": {}}], client)
    assert recovered is True
    assert client.recoveries == 1
    assert state["live_case_snapshot"]["revision"] == 3
    assert state["live_last_sequence"] == 3


def test_refresh_marks_disconnected_on_failure():
    class Offline(FakeClient):
        def get_events(self, session_id, after_sequence=0):
            raise BackendClientError("offline")

    state = {"live_session_id": "ses_1", "live_last_sequence": 0}
    with pytest.raises(BackendClientError):
        refresh_live_state(state, Offline())
    assert state["live_connection_status"] == DISCONNECTED
    assert state["live_error"] == "offline"
