from __future__ import annotations

from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.core.time import serialize_utc


class UTCModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at_utc", "updated_at_utc", "next_run_at_utc", "last_run_at_utc", check_fields=False)
    def serialize_datetime_fields(self, value: datetime | None) -> str | None:
        return serialize_utc(value)


class ScheduleCreate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    desired_state: bool
    time_local: time
    timezone: str = Field(default="America/New_York", min_length=1, max_length=80)
    rrule: str = Field(default="FREQ=DAILY", min_length=1, max_length=255)
    is_enabled: bool = True

    @field_serializer("time_local")
    def serialize_time_local(self, value: time) -> str:
        return value.strftime("%H:%M")


class ScheduleUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    desired_state: bool | None = None
    time_local: time | None = None
    timezone: str | None = Field(default=None, min_length=1, max_length=80)
    rrule: str | None = Field(default=None, min_length=1, max_length=255)
    is_enabled: bool | None = None

    @field_serializer("time_local")
    def serialize_time_local(self, value: time | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%H:%M")


class ScheduleRead(UTCModel):
    id: UUID
    device_id: UUID
    name: str | None
    desired_state: bool
    time_local: time
    timezone: str
    rrule: str
    is_enabled: bool
    next_run_at_utc: datetime | None
    last_run_at_utc: datetime | None
    created_at_utc: datetime
    updated_at_utc: datetime

    @field_serializer("time_local")
    def serialize_time_local(self, value: time) -> str:
        return value.strftime("%H:%M")


class ScheduleListResponse(BaseModel):
    items: list[ScheduleRead]
    count: int


class ScheduleDeleteResponse(BaseModel):
    ok: bool
    detail: str
    schedule_id: UUID
