from datetime import datetime, timezone

import pytest

from backend.contracts import CaseCard, CaseField, CaseUpdate, ConfirmationEvidence, FieldStatus, Handoff, HandoffState
from backend.reducer import InvalidTransition, RevisionConflict, reduce_case


def card():
    return CaseCard(case_id="case_1", session_id="ses_1")


def test_reducer_updates_field_and_revision_without_mutating_input():
    original = card()
    field = CaseField(value="73821", status=FieldStatus.CONFIRMED, confidence=.96,
                      confirmation=ConfirmationEvidence(method="read_back", confirmed_at=datetime.now(timezone.utc)))
    updated = reduce_case(original, CaseUpdate(expected_revision=0, fields={"order_id": field}))
    assert original.revision == 0
    assert updated.revision == 1
    assert updated.fields["order_id"].value == "73821"


def test_reducer_rejects_stale_revision():
    with pytest.raises(RevisionConflict):
        reduce_case(card(), CaseUpdate(expected_revision=2))


def test_reducer_rejects_skipped_handoff_transition():
    with pytest.raises(InvalidTransition):
        reduce_case(card(), CaseUpdate(expected_revision=0, handoff=Handoff(state=HandoffState.COMPLETED)))
