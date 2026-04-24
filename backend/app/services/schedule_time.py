from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import HTTPException, status

from app.core.time import ensure_utc, utc_now

SUPPORTED_RRULES = {"FREQ=DAILY"}


def validate_timezone(timezone_name: str) -> str:
    value = timezone_name.strip()
    if not value:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="timezone is required")
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"unsupported timezone: {value}",
        ) from exc
    return value


def validate_rrule(rrule: str) -> str:
    value = rrule.strip().upper()
    if value not in SUPPORTED_RRULES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="only FREQ=DAILY schedules are supported in v1",
        )
    return value


def compute_next_run_at_utc(
    *,
    time_local: time,
    timezone_name: str,
    rrule: str,
    from_utc: datetime | None = None,
) -> datetime:
    """Compute the next UTC instant from a local wall-clock schedule intent.

    Phase 6A intentionally supports daily recurrence first. The stored intent is
    local wall-clock time + IANA timezone. The execution timestamp is computed
    and stored in UTC.
    """
    validate_rrule(rrule)
    timezone_name = validate_timezone(timezone_name)

    zone = ZoneInfo(timezone_name)
    now_utc = ensure_utc(from_utc) or utc_now()
    now_local = now_utc.astimezone(zone)

    candidate_date: date = now_local.date()
    candidate_local = datetime.combine(candidate_date, time_local).replace(tzinfo=zone)

    if candidate_local <= now_local:
        candidate_local = datetime.combine(candidate_date + timedelta(days=1), time_local).replace(tzinfo=zone)

    return candidate_local.astimezone(timezone.utc)
