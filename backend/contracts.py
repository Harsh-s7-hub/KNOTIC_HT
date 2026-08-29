from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class FieldStatus(str, Enum):
    MISSING = "missing"
    CANDIDATE = "candidate"
    ASSUMED = "assumed"
    UNCERTAIN = "uncertain"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    NOT_APPLICABLE = "not_applicable"


class CaseStatus(str, Enum):
    COLLECTING = "collecting"
    READY_FOR_SUPPORT = "ready_for_support"
    HANDOFF_IN_PROGRESS = "handoff_in_progress"
    HUMAN_CONNECTED = "human_connected"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SessionStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    ENDED = "ended"
    ERROR = "error"


class HandoffState(str, Enum):
    NOT_REQUESTED = "not_requested"
    REQUESTED = "requested"
    QUEUED = "queued"
    AGENT_ASSIGNED = "agent_assigned"
    CONTEXT_DELIVERED = "context_delivered"
    HUMAN_JOINING = "human_joining"
    HUMAN_READY = "human_ready"
    TRANSFERRING = "transferring"
    COMPLETED = "completed"
    TIMED_OUT = "timed_out"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandType(str, Enum):
    END_SESSION = "end_session"
    ASK_SUGGESTED_QUESTION = "ask_suggested_question"
    REQUEST_FIELD_CONFIRMATION = "request_field_confirmation"
    REQUEST_HANDOFF = "request_handoff"
    APPROVE_HANDOFF = "approve_handoff"
    CANCEL_HANDOFF = "cancel_handoff"
    RETRY_AGENT = "retry_agent"
    ACKNOWLEDGE_EVENT = "acknowledge_event"


class EventType(str, Enum):
    SESSION_CREATED = "session.created"
    SESSION_ENDED = "session.ended"
    CASE_UPDATED = "case.updated"
    CASE_READY_FOR_HUMAN = "case.ready_for_human"
    HANDOFF_REQUESTED = "handoff.requested"
    HANDOFF_QUEUED = "handoff.queued"
    HANDOFF_CANCELLED = "handoff.cancelled"
    COMMAND_ACCEPTED = "command.accepted"


Score = float


class Consent(StrictModel):
    recording: Literal["unknown", "granted", "denied"] = "unknown"
    transcription: Literal["unknown", "granted", "denied"] = "unknown"


class Caller(StrictModel):
    external_id: str | None = None
    display_name: str | None = None
    phone_masked: str | None = None
    consent: Consent = Field(default_factory=Consent)


class LanguageShare(StrictModel):
    code: str
    share: Score = Field(ge=0, le=1)
    confidence: Score = Field(ge=0, le=1)


class LanguageProfile(StrictModel):
    primary: str | None = None
    response_language: str | None = None
    code_switching: bool = False
    distribution: list[LanguageShare] = Field(default_factory=list)

    @field_validator("distribution")
    @classmethod
    def validate_distribution(cls, value: list[LanguageShare]) -> list[LanguageShare]:
        if sum(item.share for item in value) > 1.0001:
            raise ValueError("language shares cannot total more than 1")
        return value


class ConfirmationEvidence(StrictModel):
    method: Literal["explicit_user_confirmation", "read_back", "trusted_system"]
    confirmed_at: datetime


class CaseField(StrictModel):
    value: Any = None
    status: FieldStatus = FieldStatus.MISSING
    confidence: Score = Field(default=0, ge=0, le=1)
    source_turn_ids: list[str] = Field(default_factory=list)
    confirmation: ConfirmationEvidence | None = None
    updated_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def confirmed_requires_evidence(self) -> "CaseField":
        if self.status == FieldStatus.CONFIRMED and self.confirmation is None:
            raise ValueError("confirmed fields require confirmation evidence")
        if self.status == FieldStatus.CONFIRMED and self.value is None:
            raise ValueError("confirmed fields require a value")
        return self


class ProblemAlternative(StrictModel):
    label: str
    confidence: Score = Field(ge=0, le=1)


class Problem(StrictModel):
    summary: str = ""
    category: str | None = None
    subcategory: str | None = None
    confidence: Score = Field(default=0, ge=0, le=1)
    alternatives: list[ProblemAlternative] = Field(default_factory=list)


class Assumption(StrictModel):
    id: str
    statement: str
    confidence: Score = Field(ge=0, le=1)
    source_turn_ids: list[str] = Field(default_factory=list)
    must_confirm: bool = True


class Uncertainty(StrictModel):
    id: str
    field_path: str | None = None
    reason_code: str
    severity: Literal["low", "medium", "high", "critical"]
    confidence: Score = Field(ge=0, le=1)
    resolution: str | None = None


class ConfidenceBreakdown(StrictModel):
    overall: Score = Field(default=0, ge=0, le=1)
    understanding: Score = Field(default=0, ge=0, le=1)
    extraction: Score = Field(default=0, ge=0, le=1)
    required_information: Score = Field(default=0, ge=0, le=1)
    routing: Score = Field(default=0, ge=0, le=1)
    consistency: Score = Field(default=0, ge=0, le=1)
    risk: Score = Field(default=0, ge=0, le=1)
    explanation: str = ""

    def calculated_overall(self) -> float:
        base = (0.20 * self.understanding + 0.25 * self.required_information +
                0.20 * self.extraction + 0.20 * self.routing +
                0.15 * self.consistency)
        return round(max(0.0, min(1.0, base - self.risk)), 4)


class NextAction(StrictModel):
    type: str
    field_path: str | None = None
    question: str | None = None
    reason: str
    priority: int = Field(ge=0, le=100)


class Expertise(StrictModel):
    required_skills: list[str] = Field(default_factory=list)
    department: str | None = None
    confidence: Score = Field(default=0, ge=0, le=1)


class Routing(StrictModel):
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    queue: str | None = None
    decision: Literal["undecided", "self_service", "human_required"] = "undecided"
    reason_codes: list[str] = Field(default_factory=list)
    sla_seconds: int | None = Field(default=None, ge=0)
    assigned_agent: str | None = None
    fallback_queues: list[str] = Field(default_factory=list)


class HumanAgent(StrictModel):
    agent_id: str
    display_name: str
    department: str | None = None


class Handoff(StrictModel):
    handoff_id: str | None = None
    state: HandoffState = HandoffState.NOT_REQUESTED
    reason_codes: list[str] = Field(default_factory=list)
    requested_at: datetime | None = None
    accepted_at: datetime | None = None
    completed_at: datetime | None = None
    human_agent: HumanAgent | None = None
    context_package_id: str | None = None


class SupportReadiness(StrictModel):
    ready: bool = False
    state: str = "needs_information"
    blocking_fields: list[str] = Field(default_factory=list)
    ready_at: datetime | None = None


class CaseSummary(StrictModel):
    customer_narrative: str = ""
    confirmed_facts: list[str] = Field(default_factory=list)
    unconfirmed_facts: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    actions_taken: list[str] = Field(default_factory=list)
    recommended_human_action: str | None = None


class CaseCard(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    case_id: str
    session_id: str
    revision: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    status: CaseStatus = CaseStatus.COLLECTING
    support_readiness: SupportReadiness = Field(default_factory=SupportReadiness)
    caller: Caller = Field(default_factory=Caller)
    language: LanguageProfile = Field(default_factory=LanguageProfile)
    problem: Problem = Field(default_factory=Problem)
    fields: dict[str, CaseField] = Field(default_factory=dict)
    assumptions: list[Assumption] = Field(default_factory=list)
    uncertainties: list[Uncertainty] = Field(default_factory=list)
    confidence: ConfidenceBreakdown = Field(default_factory=ConfidenceBreakdown)
    next_action: NextAction | None = None
    expertise: Expertise = Field(default_factory=Expertise)
    routing: Routing = Field(default_factory=Routing)
    handoff: Handoff = Field(default_factory=Handoff)
    summary: CaseSummary = Field(default_factory=CaseSummary)


class CaseUpdate(StrictModel):
    expected_revision: int = Field(ge=0)
    fields: dict[str, CaseField] | None = None
    confidence: ConfidenceBreakdown | None = None
    support_readiness: SupportReadiness | None = None
    handoff: Handoff | None = None
    status: CaseStatus | None = None
    routing: Routing | None = None
    next_action: NextAction | None = None


class EventEnvelope(StrictModel):
    event_id: str
    sequence: int = Field(ge=1)
    type: str
    schema_version: Literal["1.0"] = "1.0"
    session_id: str
    case_id: str
    occurred_at: datetime = Field(default_factory=utc_now)
    correlation_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class SessionCreateRequest(StrictModel):
    caller: Caller = Field(default_factory=Caller)
    locale_hints: list[str] = Field(default_factory=list)
    client: dict[str, str] = Field(default_factory=dict)


class SessionResponse(StrictModel):
    session_id: str
    case_id: str
    status: SessionStatus
    event_stream_url: str
    revision: int
    transport: None = None
    capabilities: dict[str, bool] = Field(default_factory=lambda: {"agora": False, "voice": False})


class CommandRequest(StrictModel):
    command_id: str = Field(min_length=1)
    type: CommandType
    expected_revision: int = Field(ge=0)
    payload: dict[str, Any] = Field(default_factory=dict)


class CommandResponse(StrictModel):
    command_id: str
    accepted: bool
    duplicate: bool = False
    case_revision: int
    event_ids: list[str] = Field(default_factory=list)


class TranscriptResponse(StrictModel):
    session_id: str
    turns: list[dict[str, Any]] = Field(default_factory=list)


class EventsResponse(StrictModel):
    session_id: str
    events: list[EventEnvelope]
