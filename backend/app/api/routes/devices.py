from __future__ import annotations

import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.adapters.errors import DeviceConfigurationError, DeviceConnectivityError
from app.adapters.registry import get_adapter
from app.db.models import Device, EventLog, Location
from app.db.session import get_db
from app.schemas.device import (
    DeviceConnectivityTestRequest,
    DeviceConnectivityTestResponse,
    DeviceCreate,
    DevicePowerCommandRequest,
    DevicePowerCommandResponse,
    DeviceRead,
    DeviceStatusRead,
)
from app.schemas.event_log import EventLogListResponse
from app.services.device_state_cache import build_unreachable_state, upsert_device_state_cache
from app.services.event_logs import create_event_log

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/test-connectivity", response_model=DeviceConnectivityTestResponse)
async def test_device_connectivity(
    payload: DeviceConnectivityTestRequest,
    db: Session = Depends(get_db),
) -> DeviceConnectivityTestResponse:
    try:
        adapter = get_adapter(payload.device_type)
        normalized_config = adapter.validate_config(payload.config_json)
        result = await adapter.test_connectivity(normalized_config)
    except DeviceConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except DeviceConnectivityError as exc:
        create_event_log(
            db,
            event_type="device_connectivity_test_failed",
            target_type="device_candidate",
            severity="warning",
            message="Device connectivity test failed.",
            payload_json={
                "device_type": payload.device_type,
                "config_json": payload.config_json,
                "error": str(exc),
            },
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    create_event_log(
        db,
        event_type="device_connectivity_test_passed",
        target_type="device_candidate",
        message="Device connectivity test passed.",
        payload_json={
            "device_type": payload.device_type,
            "config_json": normalized_config,
            "result": result,
        },
    )
    db.commit()
    return DeviceConnectivityTestResponse(ok=True, detail="Connectivity test passed.", result=result)


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
) -> DeviceRead:
    try:
        adapter = get_adapter(payload.device_type)
        normalized_config = adapter.validate_config(payload.config_json)
    except DeviceConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    if payload.location_id is not None:
        location = db.get(Location, payload.location_id)
        if location is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="location not found")

    device = Device(
        name=payload.name.strip(),
        device_type=payload.device_type,
        location_id=payload.location_id,
        config_json=normalized_config,
        is_enabled=payload.is_enabled,
    )
    db.add(device)
    db.flush()

    try:
        live_status = _run(adapter.get_status(normalized_config))
    except DeviceConnectivityError as exc:
        upsert_device_state_cache(
            db,
            device_id=device.id,
            status_json=build_unreachable_state(str(exc)),
            mark_seen=False,
        )
        create_event_log(
            db,
            event_type="device_created",
            target_type="device",
            target_id=device.id,
            severity="warning",
            message="Device created, but initial status fetch failed.",
            payload_json={
                "device_type": device.device_type,
                "name": device.name,
                "config_json": device.config_json,
                "error": str(exc),
            },
        )
    else:
        upsert_device_state_cache(
            db,
            device_id=device.id,
            status_json=_normalize_live_status(live_status),
            mark_seen=True,
        )
        create_event_log(
            db,
            event_type="device_created",
            target_type="device",
            target_id=device.id,
            message="Device created and initial status cached.",
            payload_json={
                "device_type": device.device_type,
                "name": device.name,
                "config_json": device.config_json,
                "initial_status": live_status,
            },
        )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="device could not be saved") from exc

    return _get_device_or_404(db, device.id)


@router.get("", response_model=list[DeviceRead])
def list_devices(db: Session = Depends(get_db)) -> list[DeviceRead]:
    stmt = select(Device).options(selectinload(Device.state_cache)).order_by(Device.created_at_utc.desc())
    return list(db.scalars(stmt).all())


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: UUID, db: Session = Depends(get_db)) -> DeviceRead:
    return _get_device_or_404(db, device_id)


@router.get("/{device_id}/status", response_model=DeviceStatusRead)
async def get_device_status(device_id: UUID, db: Session = Depends(get_db)) -> DeviceStatusRead:
    device = _get_device_or_404(db, device_id)

    try:
        adapter = get_adapter(device.device_type)
        status_payload = await adapter.get_status(device.config_json)
    except (DeviceConfigurationError, DeviceConnectivityError) as exc:
        upsert_device_state_cache(
            db,
            device_id=device.id,
            status_json=build_unreachable_state(str(exc)),
            mark_seen=False,
        )
        create_event_log(
            db,
            event_type="device_status_refresh_failed",
            target_type="device",
            target_id=device.id,
            severity="warning",
            message="Device status refresh failed.",
            payload_json={"error": str(exc)},
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    normalized_status = _normalize_live_status(status_payload)
    upsert_device_state_cache(db, device_id=device.id, status_json=normalized_status, mark_seen=True)
    create_event_log(
        db,
        event_type="device_status_refreshed",
        target_type="device",
        target_id=device.id,
        message="Device status refreshed.",
        payload_json={"status": normalized_status},
    )
    db.commit()
    return DeviceStatusRead(device_id=device.id, status=normalized_status)


@router.get("/{device_id}/event-logs", response_model=EventLogListResponse)
def list_device_event_logs(
    device_id: UUID,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
) -> EventLogListResponse:
    _get_device_or_404(db, device_id)
    stmt = (
        select(EventLog)
        .where(EventLog.target_type == "device", EventLog.target_id == device_id)
        .order_by(EventLog.created_at_utc.desc())
        .limit(limit)
    )
    items = list(db.scalars(stmt).all())
    return EventLogListResponse(items=items, count=len(items))


@router.post("/{device_id}/commands/power", response_model=DevicePowerCommandResponse)
async def set_device_power(
    device_id: UUID,
    payload: DevicePowerCommandRequest,
    db: Session = Depends(get_db),
) -> DevicePowerCommandResponse:
    device = _get_device_or_404(db, device_id)
    if not device.is_enabled:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="device is disabled")

    try:
        adapter = get_adapter(device.device_type)
        result = await adapter.set_state(device.config_json, {"on": payload.on})
    except (DeviceConfigurationError, DeviceConnectivityError) as exc:
        upsert_device_state_cache(
            db,
            device_id=device.id,
            status_json=build_unreachable_state(str(exc)),
            mark_seen=False,
        )
        create_event_log(
            db,
            event_type="device_power_command_failed",
            target_type="device",
            target_id=device.id,
            severity="warning",
            message="Device power command failed.",
            payload_json={"requested_on": payload.on, "error": str(exc)},
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    normalized_status = _normalize_live_status(result["status"])
    upsert_device_state_cache(db, device_id=device.id, status_json=normalized_status, mark_seen=True)
    create_event_log(
        db,
        event_type="device_power_command_sent",
        target_type="device",
        target_id=device.id,
        message="Device power command sent.",
        payload_json={
            "requested_on": payload.on,
            "status": normalized_status,
            "command_result": result.get("command_result"),
        },
    )
    db.commit()

    return DevicePowerCommandResponse(
        ok=True,
        detail="Power command succeeded.",
        device_id=device.id,
        status=normalized_status,
    )


def _get_device_or_404(db: Session, device_id: UUID) -> Device:
    stmt = select(Device).options(selectinload(Device.state_cache)).where(Device.id == device_id)
    device = db.scalars(stmt).one_or_none()
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="device not found")
    return device


def _normalize_live_status(status: dict) -> dict:
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


def _run(coro):
    return asyncio.run(coro)
