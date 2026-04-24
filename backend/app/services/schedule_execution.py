from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.errors import DeviceConfigurationError, DeviceConnectivityError
from app.adapters.registry import get_adapter
from app.core.time import ensure_utc, utc_now
from app.db.models import Device, Schedule
from app.services.device_state_cache import build_unreachable_state, upsert_device_state_cache
from app.services.event_logs import create_event_log


@dataclass(slots=True)
class ScheduleExecutionResult:
    schedule_id: UUID
    device_id: UUID | None
    status: str
    message: str
    next_run_at_utc: datetime | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SchedulerTickResult:
    checked_at_utc: datetime
    due_count: int
    results: list[ScheduleExecutionResult]


def get_due_schedules(db: Session, *, now_utc: datetime | None = None, limit: int = 25) -> list[Schedule]:
    """Return enabled schedules due for execution.

    Uses SKIP LOCKED on Postgres so multiple orchestrator processes do not grab
    the exact same due schedule rows at the same time.
    """
    now_utc = ensure_utc(now_utc) or utc_now()

    stmt = (
        select(Schedule)
        .where(
            Schedule.is_enabled.is_(True),
            Schedule.next_run_at_utc.is_not(None),
            Schedule.next_run_at_utc <= now_utc,
        )
        .order_by(Schedule.next_run_at_utc.asc(), Schedule.created_at_utc.asc())
        .limit(limit)
        .with_for_update(skip_locked=True)
    )
    return list(db.scalars(stmt).all())


async def run_scheduler_tick(db: Session, *, batch_size: int = 25) -> SchedulerTickResult:
    """Execute one scheduler polling pass.

    This is intentionally independent of FastAPI. The console orchestrator calls
    this repeatedly, and tests/dev commands can call it once.
    """
    checked_at_utc = utc_now()
    due_schedules = get_due_schedules(db, now_utc=checked_at_utc, limit=batch_size)
    results: list[ScheduleExecutionResult] = []

    for schedule in due_schedules:
        result = await execute_due_schedule(db, schedule, now_utc=checked_at_utc)
        results.append(result)
        db.commit()

    return SchedulerTickResult(
        checked_at_utc=checked_at_utc,
        due_count=len(due_schedules),
        results=results,
    )


async def execute_due_schedule(
    db: Session,
    schedule: Schedule,
    *,
    now_utc: datetime | None = None,
) -> ScheduleExecutionResult:
    """Execute a single due schedule and advance it to its next UTC run.

    Failure still advances the schedule. That prevents an offline plug from being
    hammered every scheduler tick forever. The failed execution is preserved in
    event_logs for debugging.
    """
    now_utc = ensure_utc(now_utc) or utc_now()
    device = db.get(Device, schedule.device_id)

    if device is None:
        next_run = compute_next_run_at_utc(schedule, after_utc=now_utc)
        schedule.last_run_at_utc = now_utc
        schedule.next_run_at_utc = next_run
        create_event_log(
            db,
            event_type="schedule_execution_skipped",
            target_type="schedule",
            target_id=schedule.id,
            severity="warning",
            message="Schedule skipped because device was not found.",
            payload_json={
                "schedule_id": str(schedule.id),
                "device_id": str(schedule.device_id),
                "next_run_at_utc": _iso_utc(next_run),
            },
        )
        return ScheduleExecutionResult(
            schedule_id=schedule.id,
            device_id=schedule.device_id,
            status="skipped",
            message="device not found",
            next_run_at_utc=next_run,
        )

    if not device.is_enabled:
        next_run = compute_next_run_at_utc(schedule, after_utc=now_utc)
        schedule.last_run_at_utc = now_utc
        schedule.next_run_at_utc = next_run
        create_event_log(
            db,
            event_type="schedule_execution_skipped",
            target_type="schedule",
            target_id=schedule.id,
            severity="warning",
            message="Schedule skipped because device is disabled.",
            payload_json={
                "schedule_id": str(schedule.id),
                "device_id": str(device.id),
                "device_name": device.name,
                "next_run_at_utc": _iso_utc(next_run),
            },
        )
        return ScheduleExecutionResult(
            schedule_id=schedule.id,
            device_id=device.id,
            status="skipped",
            message="device disabled",
            next_run_at_utc=next_run,
        )

    requested_on = bool(schedule.desired_state)

    try:
        adapter = get_adapter(device.device_type)
        command_result = await adapter.set_state(device.config_json, {"on": requested_on})
        normalized_status = normalize_live_status(command_result["status"])
        upsert_device_state_cache(
            db,
            device_id=device.id,
            status_json=normalized_status,
            mark_seen=True,
        )

        next_run = compute_next_run_at_utc(schedule, after_utc=now_utc)
        schedule.last_run_at_utc = now_utc
        schedule.next_run_at_utc = next_run

        create_event_log(
            db,
            event_type="schedule_execution_succeeded",
            target_type="schedule",
            target_id=schedule.id,
            severity="info",
            message="Scheduled device command succeeded.",
            payload_json={
                "schedule_id": str(schedule.id),
                "schedule_name": schedule.name,
                "device_id": str(device.id),
                "device_name": device.name,
                "requested_on": requested_on,
                "status": normalized_status,
                "command_result": command_result.get("command_result"),
                "last_run_at_utc": _iso_utc(now_utc),
                "next_run_at_utc": _iso_utc(next_run),
            },
        )
        return ScheduleExecutionResult(
            schedule_id=schedule.id,
            device_id=device.id,
            status="succeeded",
            message="scheduled command succeeded",
            next_run_at_utc=next_run,
            payload={"requested_on": requested_on, "status": normalized_status},
        )

    except (DeviceConfigurationError, DeviceConnectivityError, Exception) as exc:
        error_text = f"{exc.__class__.__name__}: {exc}"
        upsert_device_state_cache(
            db,
            device_id=device.id,
            status_json=build_unreachable_state(error_text),
            mark_seen=False,
        )

        next_run = compute_next_run_at_utc(schedule, after_utc=now_utc)
        schedule.last_run_at_utc = now_utc
        schedule.next_run_at_utc = next_run

        create_event_log(
            db,
            event_type="schedule_execution_failed",
            target_type="schedule",
            target_id=schedule.id,
            severity="warning",
            message="Scheduled device command failed.",
            payload_json={
                "schedule_id": str(schedule.id),
                "schedule_name": schedule.name,
                "device_id": str(device.id),
                "device_name": device.name,
                "requested_on": requested_on,
                "error": error_text,
                "last_run_at_utc": _iso_utc(now_utc),
                "next_run_at_utc": _iso_utc(next_run),
            },
        )
        return ScheduleExecutionResult(
            schedule_id=schedule.id,
            device_id=device.id,
            status="failed",
            message=error_text,
            next_run_at_utc=next_run,
            payload={"requested_on": requested_on, "error": error_text},
        )


def compute_next_run_at_utc(schedule: Schedule, *, after_utc: datetime | None = None) -> datetime:
    """Compute the next UTC run from the schedule's local intent.

    V1 supports the current schedule contract: daily wall-clock schedules.
    The schedule stores local time + IANA timezone. The runner computes UTC.
    """
    after_utc = ensure_utc(after_utc) or utc_now()
    recurrence = (schedule.rrule or "FREQ=DAILY").upper().strip()
    if recurrence != "FREQ=DAILY":
        raise ValueError(f"unsupported rrule for scheduler execution: {schedule.rrule}")

    tz = _zoneinfo(schedule.timezone)
    local_after = after_utc.astimezone(tz)
    target_time = _coerce_time(schedule.time_local)

    candidate_date = local_after.date()
    candidate_local = _local_datetime(candidate_date, target_time, tz)

    if candidate_local <= local_after:
        candidate_local = _local_datetime(candidate_date + timedelta(days=1), target_time, tz)

    return candidate_local.astimezone(timezone.utc)


def normalize_live_status(status: dict[str, Any]) -> dict[str, Any]:
    return {
        "reachable": bool(status.get("reachable", False)),
        "host": status.get("host"),
        "switch_id": status.get("switch_id"),
        "output": status.get("output"),
        "apower": status.get("apower"),
        "voltage": status.get("voltage"),
        "current": status.get("current"),
        "errors": status.get("errors", []),
        "last_error": status.get("last_error"),
        "raw": status.get("raw", {}),
    }


def _zoneinfo(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"invalid IANA timezone: {timezone_name}") from exc


def _coerce_time(value: time | str) -> time:
    if isinstance(value, time):
        return value.replace(tzinfo=None)
    if isinstance(value, str):
        return time.fromisoformat(value).replace(tzinfo=None)
    raise TypeError(f"unsupported time_local value: {value!r}")


def _local_datetime(day: date, local_time: time, tz: ZoneInfo) -> datetime:
    return datetime.combine(day, local_time).replace(tzinfo=tz)


def _iso_utc(value: datetime | None) -> str | None:
    if value is None:
        return None
    return ensure_utc(value).isoformat().replace("+00:00", "Z")
