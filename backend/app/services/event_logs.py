from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import EventLog


def create_event_log(
    db: Session,
    *,
    event_type: str,
    target_type: str,
    message: str,
    severity: str = "info",
    target_id: UUID | None = None,
    payload_json: dict[str, Any] | None = None,
) -> EventLog:
    event = EventLog(
        event_type=event_type,
        target_type=target_type,
        target_id=target_id,
        severity=severity,
        message=message,
        payload_json=payload_json,
    )
    db.add(event)
    return event
