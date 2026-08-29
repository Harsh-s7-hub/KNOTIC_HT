from __future__ import annotations

from copy import deepcopy

from backend.contracts import CaseCard, CaseUpdate, FieldStatus, HandoffState, utc_now


class RevisionConflict(ValueError):
    pass


class InvalidTransition(ValueError):
    pass


HANDOFF_TRANSITIONS = {
    HandoffState.NOT_REQUESTED: {HandoffState.REQUESTED},
    HandoffState.REQUESTED: {HandoffState.QUEUED, HandoffState.CANCELLED, HandoffState.FAILED},
    HandoffState.QUEUED: {HandoffState.AGENT_ASSIGNED, HandoffState.CANCELLED, HandoffState.TIMED_OUT, HandoffState.FAILED},
    HandoffState.AGENT_ASSIGNED: {HandoffState.CONTEXT_DELIVERED, HandoffState.CANCELLED, HandoffState.FAILED},
    HandoffState.CONTEXT_DELIVERED: {HandoffState.HUMAN_JOINING, HandoffState.FAILED},
    HandoffState.HUMAN_JOINING: {HandoffState.HUMAN_READY, HandoffState.FAILED},
    HandoffState.HUMAN_READY: {HandoffState.TRANSFERRING, HandoffState.FAILED},
    HandoffState.TRANSFERRING: {HandoffState.COMPLETED, HandoffState.FAILED},
    HandoffState.TIMED_OUT: {HandoffState.QUEUED, HandoffState.CANCELLED},
    HandoffState.FAILED: {HandoffState.REQUESTED, HandoffState.CANCELLED},
    HandoffState.CANCELLED: {HandoffState.REQUESTED},
    HandoffState.COMPLETED: set(),
}


def reduce_case(card: CaseCard, update: CaseUpdate) -> CaseCard:
    if update.expected_revision != card.revision:
        raise RevisionConflict(f"expected revision {update.expected_revision}, current revision is {card.revision}")

    result = deepcopy(card)
    if update.fields is not None:
        for path, field in update.fields.items():
            if not path.strip():
                raise ValueError("field paths cannot be blank")
            if field.status == FieldStatus.CONFIRMED and field.confirmation is None:
                raise ValueError("confirmed fields require evidence")
            result.fields[path] = field

    if update.handoff is not None:
        old_state = HandoffState(result.handoff.state)
        new_state = HandoffState(update.handoff.state)
        if new_state != old_state and new_state not in HANDOFF_TRANSITIONS[old_state]:
            raise InvalidTransition(f"handoff cannot transition from {old_state.value} to {new_state.value}")
        result.handoff = update.handoff

    for name in ("confidence", "support_readiness", "status", "routing", "next_action"):
        value = getattr(update, name)
        if value is not None:
            setattr(result, name, value)

    result.revision += 1
    result.updated_at = utc_now()
    return CaseCard.model_validate(result.model_dump())
