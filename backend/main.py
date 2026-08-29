from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.contracts import (
    CaseCard, CaseStatus, CaseUpdate, CommandRequest, CommandResponse, CommandType,
    EventType, EventsResponse, Handoff, HandoffState, Routing, SessionCreateRequest,
    SessionResponse, SessionStatus, TranscriptResponse, utc_now,
)
from backend.reducer import InvalidTransition, RevisionConflict, reduce_case
from backend.store import InMemoryStore, SessionRecord


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = InMemoryStore()
    yield


app = FastAPI(title="EchoSphere Backend", version="0.1.0", lifespan=lifespan)


def error(status: int, code: str, message: str, details=None) -> HTTPException:
    return HTTPException(status_code=status, detail={"code": code, "message": message, "details": details})


@app.exception_handler(HTTPException)
async def http_error(_: Request, exc: HTTPException):
    body = exc.detail if isinstance(exc.detail, dict) else {"code": "HTTP_ERROR", "message": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content={"error": body})


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": {"code": "VALIDATION_ERROR", "message": "Request validation failed", "details": exc.errors()}})


def store(request: Request) -> InMemoryStore:
    return request.app.state.store


def get_session(repo: InMemoryStore, session_id: str) -> SessionRecord:
    record = repo.sessions.get(session_id)
    if record is None:
        raise error(404, "SESSION_NOT_FOUND", f"Session {session_id} does not exist")
    return record


@app.get("/health")
async def health():
    return {"status": "ok", "service": "echosphere-backend"}


@app.get("/ready")
async def ready():
    return {"status": "ready", "dependencies": {"in_memory_store": "ok"}, "capabilities": {"agora": False, "voice": False}}


@app.post("/api/v1/sessions", response_model=SessionResponse, status_code=201)
async def create_session(body: SessionCreateRequest, request: Request,
                         idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    repo = store(request)
    if idempotency_key:
        cached = repo.commands.get(("create_session", idempotency_key))
        if cached:
            return cached
    session_id, case_id = f"ses_{uuid4().hex}", f"case_{uuid4().hex}"
    card = CaseCard(case_id=case_id, session_id=session_id, caller=body.caller)
    record = SessionRecord(session_id=session_id, case_id=case_id, status=SessionStatus.CREATED, case=card)
    repo.sessions[session_id] = record
    await repo.publish(session_id, case_id, EventType.SESSION_CREATED.value,
                       {"status": SessionStatus.CREATED.value, "case_revision": 0})
    response = SessionResponse(session_id=session_id, case_id=case_id, status=record.status,
                               event_stream_url=f"/api/v1/sessions/{session_id}/events", revision=0)
    if idempotency_key:
        repo.commands[("create_session", idempotency_key)] = response
    return response


@app.get("/api/v1/sessions/{session_id}/case", response_model=CaseCard)
async def case_snapshot(session_id: str, request: Request):
    return get_session(store(request), session_id).case


@app.get("/api/v1/cases/{case_id}", response_model=CaseCard)
async def case_by_id(case_id: str, request: Request):
    for record in store(request).sessions.values():
        if record.case_id == case_id:
            return record.case
    raise error(404, "CASE_NOT_FOUND", f"Case {case_id} does not exist")


@app.get("/api/v1/sessions/{session_id}/transcript", response_model=TranscriptResponse)
async def transcript(session_id: str, request: Request):
    record = get_session(store(request), session_id)
    return TranscriptResponse(session_id=session_id, turns=record.transcript)


@app.get("/api/v1/sessions/{session_id}/handoff", response_model=Handoff)
async def handoff(session_id: str, request: Request):
    return get_session(store(request), session_id).case.handoff


@app.get("/api/v1/sessions/{session_id}/events", response_model=EventsResponse)
async def events(session_id: str, request: Request, after_sequence: int = Query(default=0, ge=0)):
    repo = store(request)
    get_session(repo, session_id)
    return EventsResponse(session_id=session_id,
                          events=[event for event in repo.events.get(session_id, []) if event.sequence > after_sequence])


@app.post("/api/v1/sessions/{session_id}/commands", response_model=CommandResponse)
async def command(session_id: str, body: CommandRequest, request: Request,
                  idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    repo = store(request)
    record = get_session(repo, session_id)
    key = (session_id, idempotency_key or body.command_id)
    if key in repo.commands:
        saved = repo.commands[key]
        return saved.model_copy(update={"duplicate": True})
    if body.expected_revision != record.case.revision:
        raise error(409, "REVISION_CONFLICT", "Command targets a stale Case Card revision",
                    {"expected": body.expected_revision, "current": record.case.revision})

    event_ids: list[str] = []
    initial_revision = record.case.revision
    try:
        if body.type == CommandType.REQUEST_HANDOFF:
            reason = str(body.payload.get("reason_code", "operator_requested"))
            now = utc_now()
            handoff_model = Handoff(handoff_id=f"handoff_{uuid4().hex}", state=HandoffState.REQUESTED,
                                    reason_codes=[reason], requested_at=now,
                                    context_package_id=f"ctx_{uuid4().hex}")
            routing = record.case.routing.model_copy(update={"decision": "human_required"})
            record.case = reduce_case(record.case, CaseUpdate(expected_revision=record.case.revision,
                handoff=handoff_model, status=CaseStatus.HANDOFF_IN_PROGRESS, routing=Routing.model_validate(routing)))
            evt = await repo.publish(session_id, record.case_id, EventType.HANDOFF_REQUESTED.value,
                                     {"handoff": record.case.handoff.model_dump(mode="json"), "case_revision": record.case.revision}, body.command_id)
            event_ids.append(evt.event_id)
        elif body.type == CommandType.APPROVE_HANDOFF:
            queued = record.case.handoff.model_copy(update={"state": HandoffState.QUEUED})
            record.case = reduce_case(record.case, CaseUpdate(expected_revision=record.case.revision, handoff=queued))
            evt = await repo.publish(session_id, record.case_id, EventType.HANDOFF_QUEUED.value,
                                     {"handoff": record.case.handoff.model_dump(mode="json"), "case_revision": record.case.revision}, body.command_id)
            event_ids.append(evt.event_id)
        elif body.type == CommandType.CANCEL_HANDOFF:
            cancelled = record.case.handoff.model_copy(update={"state": HandoffState.CANCELLED})
            record.case = reduce_case(record.case, CaseUpdate(expected_revision=record.case.revision,
                                                               handoff=cancelled, status=CaseStatus.COLLECTING))
            evt = await repo.publish(session_id, record.case_id, EventType.HANDOFF_CANCELLED.value,
                                     {"handoff": record.case.handoff.model_dump(mode="json"), "case_revision": record.case.revision}, body.command_id)
            event_ids.append(evt.event_id)
        elif body.type == CommandType.END_SESSION:
            if record.status == SessionStatus.ENDED:
                raise error(409, "SESSION_ALREADY_ENDED", "Session is already ended")
            record.status = SessionStatus.ENDED
            record.case = reduce_case(record.case, CaseUpdate(expected_revision=record.case.revision, status=CaseStatus.CLOSED))
            evt = await repo.publish(session_id, record.case_id, EventType.SESSION_ENDED.value,
                                     {"status": "ended", "case_revision": record.case.revision}, body.command_id)
            event_ids.append(evt.event_id)
        else:
            evt = await repo.publish(session_id, record.case_id, EventType.COMMAND_ACCEPTED.value,
                                     {"command_type": body.type, "case_revision": record.case.revision}, body.command_id)
            event_ids.append(evt.event_id)
    except RevisionConflict as exc:
        raise error(409, "REVISION_CONFLICT", str(exc)) from exc
    except InvalidTransition as exc:
        raise error(409, "INVALID_HANDOFF_TRANSITION", str(exc)) from exc

    if record.case.revision != initial_revision:
        case_event = await repo.publish(
            session_id,
            record.case_id,
            EventType.CASE_UPDATED.value,
            {
                "previous_revision": initial_revision,
                "revision": record.case.revision,
                "snapshot": record.case.model_dump(mode="json"),
            },
            body.command_id,
        )
        event_ids.append(case_event.event_id)

    response = CommandResponse(command_id=body.command_id, accepted=True,
                               case_revision=record.case.revision, event_ids=event_ids)
    repo.commands[key] = response
    return response


@app.websocket("/api/v1/sessions/{session_id}/ws")
async def websocket_events(websocket: WebSocket, session_id: str, after_sequence: int = 0):
    repo: InMemoryStore = websocket.app.state.store
    if session_id not in repo.sessions:
        await websocket.close(code=4404, reason="session not found")
        return
    await websocket.accept()
    queue = repo.subscribe(session_id)
    try:
        for event in repo.events.get(session_id, []):
            if event.sequence > after_sequence:
                await websocket.send_json(event.model_dump(mode="json"))
        while True:
            event = await queue.get()
            await websocket.send_json(event.model_dump(mode="json"))
    except WebSocketDisconnect:
        pass
    finally:
        repo.unsubscribe(session_id, queue)


def unavailable(feature: str):
    raise error(501, "NOT_IMPLEMENTED", f"{feature} is intentionally unavailable before the Agora phase")


@app.post("/api/v1/sessions/{session_id}/agent:start")
async def agent_start(session_id: str, request: Request):
    get_session(store(request), session_id)
    unavailable("Agent start")


@app.post("/api/v1/sessions/{session_id}/agent:stop")
async def agent_stop(session_id: str, request: Request):
    get_session(store(request), session_id)
    unavailable("Agent stop")


@app.post("/api/v1/sessions/{session_id}/token:refresh")
async def token_refresh(session_id: str, request: Request):
    get_session(store(request), session_id)
    unavailable("RTC token refresh")


@app.post("/api/v1/webhooks/agora")
async def agora_webhook():
    unavailable("Agora webhooks")
