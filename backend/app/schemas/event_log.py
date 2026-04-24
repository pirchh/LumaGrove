from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.core.time import serialize_utc


class EventLogRead(BaseModel):
    id: UUID
    event_type: str
    target_type: str
    target_id: UUID | None
    severity: str
    message: str
    payload_json: dict[str, Any] | None
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at_utc")
    def serialize_created_at(self, value: datetime) -> str:
        return serialize_utc(value) or ""


class EventLogListResponse(BaseModel):
    items: list[EventLogRead]
    count: int = Field(ge=0)
