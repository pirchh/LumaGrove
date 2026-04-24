from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Device, Schedule
from app.db.session import get_db
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleDeleteResponse,
    ScheduleListResponse,
    ScheduleRead,
    ScheduleUpdate,
)
from app.services.event_logs import create_event_log
from app.services.schedule_time import compute_next_run_at_utc, validate_rrule, validate_timezone

router = APIRouter(tags=["schedules"])


@router.post("/devices/{device_id}/schedules", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
def create_device_schedule(
    device_id: UUID,
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
) -> ScheduleRead:
    device = _get_device_or_404(db, device_id)
    timezone_name = validate_timezone(payload.timezone)
    rrule = validate_rrule(payload.rrule)
    next_run_at_utc = (
        compute_next_run_at_utc(
            time_local=payload.time_local,
            timezone_name=timezone_name,
            rrule=rrule,
        )
        if payload.is_enabled
        else None
    )

    schedule = Schedule(
        device_id=device.id,
        name=payload.name.strip() if payload.name else None,
        desired_state=payload.desired_state,
        time_local=payload.time_local,
        timezone=timezone_name,
        rrule=rrule,
        is_enabled=payload.is_enabled,
        next_run_at_utc=next_run_at_utc,
    )
    db.add(schedule)
    db.flush()

    create_event_log(
        db,
        event_type="schedule_created",
        target_type="schedule",
        target_id=schedule.id,
        message="Schedule created.",
        payload_json={
            "device_id": str(device.id),
            "name": schedule.name,
            "desired_state": schedule.desired_state,
            "time_local": schedule.time_local.strftime("%H:%M"),
            "timezone": schedule.timezone,
            "rrule": schedule.rrule,
            "is_enabled": schedule.is_enabled,
            "next_run_at_utc": schedule.next_run_at_utc.isoformat() if schedule.next_run_at_utc else None,
        },
    )
    db.commit()
    db.refresh(schedule)
    return schedule


@router.get("/devices/{device_id}/schedules", response_model=ScheduleListResponse)
def list_device_schedules(
    device_id: UUID,
    db: Session = Depends(get_db),
    include_disabled: bool = Query(default=True),
) -> ScheduleListResponse:
    _get_device_or_404(db, device_id)
    stmt = select(Schedule).where(Schedule.device_id == device_id).order_by(Schedule.time_local.asc())
    if not include_disabled:
        stmt = stmt.where(Schedule.is_enabled.is_(True))
    items = list(db.scalars(stmt).all())
    return ScheduleListResponse(items=items, count=len(items))


@router.get("/schedules", response_model=ScheduleListResponse)
def list_schedules(
    db: Session = Depends(get_db),
    device_id: UUID | None = Query(default=None),
    enabled: bool | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> ScheduleListResponse:
    stmt = select(Schedule).options(selectinload(Schedule.device)).order_by(Schedule.next_run_at_utc.asc().nulls_last())
    if device_id is not None:
        stmt = stmt.where(Schedule.device_id == device_id)
    if enabled is not None:
        stmt = stmt.where(Schedule.is_enabled.is_(enabled))
    stmt = stmt.limit(limit)
    items = list(db.scalars(stmt).all())
    return ScheduleListResponse(items=items, count=len(items))


@router.get("/schedules/{schedule_id}", response_model=ScheduleRead)
def get_schedule(schedule_id: UUID, db: Session = Depends(get_db)) -> ScheduleRead:
    return _get_schedule_or_404(db, schedule_id)


@router.patch("/schedules/{schedule_id}", response_model=ScheduleRead)
def update_schedule(
    schedule_id: UUID,
    payload: ScheduleUpdate,
    db: Session = Depends(get_db),
) -> ScheduleRead:
    schedule = _get_schedule_or_404(db, schedule_id)
    changes = payload.model_dump(exclude_unset=True)

    if "name" in changes:
        schedule.name = payload.name.strip() if payload.name else None
    if "desired_state" in changes and payload.desired_state is not None:
        schedule.desired_state = payload.desired_state
    if "time_local" in changes and payload.time_local is not None:
        schedule.time_local = payload.time_local
    if "timezone" in changes and payload.timezone is not None:
        schedule.timezone = validate_timezone(payload.timezone)
    if "rrule" in changes and payload.rrule is not None:
        schedule.rrule = validate_rrule(payload.rrule)
    if "is_enabled" in changes and payload.is_enabled is not None:
        schedule.is_enabled = payload.is_enabled

    schedule.next_run_at_utc = (
        compute_next_run_at_utc(
            time_local=schedule.time_local,
            timezone_name=schedule.timezone,
            rrule=schedule.rrule,
        )
        if schedule.is_enabled
        else None
    )

    create_event_log(
        db,
        event_type="schedule_updated",
        target_type="schedule",
        target_id=schedule.id,
        message="Schedule updated.",
        payload_json={
            "device_id": str(schedule.device_id),
            "changes": _json_safe_changes(changes),
            "next_run_at_utc": schedule.next_run_at_utc.isoformat() if schedule.next_run_at_utc else None,
        },
    )
    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/schedules/{schedule_id}", response_model=ScheduleDeleteResponse)
def delete_schedule(schedule_id: UUID, db: Session = Depends(get_db)) -> ScheduleDeleteResponse:
    schedule = _get_schedule_or_404(db, schedule_id)
    db.delete(schedule)
    create_event_log(
        db,
        event_type="schedule_deleted",
        target_type="schedule",
        target_id=schedule.id,
        message="Schedule deleted.",
        payload_json={"device_id": str(schedule.device_id)},
    )
    db.commit()
    return ScheduleDeleteResponse(ok=True, detail="Schedule deleted.", schedule_id=schedule_id)


def _get_device_or_404(db: Session, device_id: UUID) -> Device:
    device = db.get(Device, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="device not found")
    return device


def _get_schedule_or_404(db: Session, schedule_id: UUID) -> Schedule:
    schedule = db.get(Schedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="schedule not found")
    return schedule


def _json_safe_changes(changes: dict) -> dict:
    safe = {}
    for key, value in changes.items():
        if hasattr(value, "isoformat"):
            safe[key] = value.isoformat()
        else:
            safe[key] = value
    return safe
