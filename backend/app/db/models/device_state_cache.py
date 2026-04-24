from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DeviceStateCache(Base):
    __tablename__ = "device_state_cache"

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        primary_key=True,
    )
    status_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    last_seen_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    device = relationship("Device", back_populates="state_cache")
