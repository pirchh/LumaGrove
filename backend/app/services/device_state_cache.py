from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.db.models import DeviceStateCache


def upsert_device_state_cache(
    db: Session,
    *,
    device_id: UUID,
    status_json: dict[str, Any],
    mark_seen: bool = True,
) -> DeviceStateCache:
    state_cache = db.get(DeviceStateCache, device_id)
    if state_cache is None:
        state_cache = DeviceStateCache(device_id=device_id, status_json=status_json)
        db.add(state_cache)
    else:
        state_cache.status_json = status_json

    if mark_seen:
        state_cache.last_seen_at_utc = utc_now()

    return state_cache


def build_unreachable_state(error: str | None) -> dict[str, Any]:
    errors = [error] if error else []
    return {
        "reachable": False,
        "errors": errors,
        "last_error": error,
    }
