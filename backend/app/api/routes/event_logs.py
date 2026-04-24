from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import EventLog
from app.db.session import get_db
from app.schemas.event_log import EventLogListResponse

router = APIRouter(prefix="/event-logs", tags=["event-logs"])


@router.get("", response_model=EventLogListResponse)
def list_event_logs(
    db: Session = Depends(get_db),
    target_type: str | None = Query(default=None),
    target_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> EventLogListResponse:
    stmt = select(EventLog).order_by(EventLog.created_at_utc.desc()).limit(limit)

    if target_type is not None:
        stmt = stmt.where(EventLog.target_type == target_type)

    if target_id is not None:
        stmt = stmt.where(EventLog.target_id == target_id)

    items = list(db.scalars(stmt).all())
    return EventLogListResponse(items=items, count=len(items))
