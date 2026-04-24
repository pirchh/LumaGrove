from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.core.time import serialize_utc


class UTCModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at_utc", "updated_at_utc", "last_seen_at_utc", check_fields=False)
    def serialize_datetime_fields(self, value: datetime | None) -> str | None:
        return serialize_utc(value)


class DeviceStateCacheRead(UTCModel):
    device_id: UUID
    status_json: dict[str, Any]
    last_seen_at_utc: datetime | None
    updated_at_utc: datetime


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    device_type: str = Field(min_length=1, max_length=80)
    location_id: UUID | None = None
    config_json: dict[str, Any]
    is_enabled: bool = True


class DeviceRead(UTCModel):
    id: UUID
    name: str
    device_type: str
    location_id: UUID | None
    config_json: dict[str, Any]
    is_enabled: bool
    created_at_utc: datetime
    updated_at_utc: datetime
    state_cache: DeviceStateCacheRead | None = None


class DeviceConnectivityTestRequest(BaseModel):
    device_type: str = Field(min_length=1, max_length=80)
    config_json: dict[str, Any]


class DeviceConnectivityTestResponse(BaseModel):
    ok: bool
    detail: str
    result: dict[str, Any]


class DeviceStatusRead(BaseModel):
    device_id: UUID
    status: dict[str, Any]


class DevicePowerCommandRequest(BaseModel):
    on: bool


class DevicePowerCommandResponse(BaseModel):
    ok: bool
    detail: str
    device_id: UUID
    status: dict[str, Any]
