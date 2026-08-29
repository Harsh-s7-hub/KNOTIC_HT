from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from backend.contracts import CaseCard, EventEnvelope, SessionStatus, utc_now


@dataclass
class SessionRecord:
    session_id: str
    case_id: str
    status: SessionStatus
    case: CaseCard
    transcript: list[dict[str, Any]] = field(default_factory=list)


class InMemoryStore:
    def __init__(self) -> None:
        self.sessions: dict[str, SessionRecord] = {}
        self.events: dict[str, list[EventEnvelope]] = {}
        self.commands: dict[tuple[str, str], Any] = {}
        self.subscribers: dict[str, set[asyncio.Queue[EventEnvelope]]] = {}
        self.lock = asyncio.Lock()

    async def publish(self, session_id: str, case_id: str, event_type: str,
                      payload: dict[str, Any], correlation_id: str | None = None) -> EventEnvelope:
        from uuid import uuid4
        async with self.lock:
            stream = self.events.setdefault(session_id, [])
            event = EventEnvelope(event_id=f"evt_{uuid4().hex}", sequence=len(stream) + 1,
                                  type=event_type, session_id=session_id, case_id=case_id,
                                  occurred_at=utc_now(), correlation_id=correlation_id, payload=payload)
            stream.append(event)
            queues = list(self.subscribers.get(session_id, set()))
        for queue in queues:
            queue.put_nowait(event)
        return event

    def subscribe(self, session_id: str) -> asyncio.Queue[EventEnvelope]:
        queue: asyncio.Queue[EventEnvelope] = asyncio.Queue()
        self.subscribers.setdefault(session_id, set()).add(queue)
        return queue

    def unsubscribe(self, session_id: str, queue: asyncio.Queue[EventEnvelope]) -> None:
        self.subscribers.get(session_id, set()).discard(queue)
