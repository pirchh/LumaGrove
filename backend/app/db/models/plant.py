from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Plant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "plants"

    common_name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    latin_name: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    slug: Mapped[str] = mapped_column(String(180), nullable=False, unique=True, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    origin_region: Mapped[str | None] = mapped_column(String(160), nullable=True)
    growth_zones: Mapped[str | None] = mapped_column(String(160), nullable=True)
    light_preference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    water_preference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    humidity_preference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    temperature_range: Mapped[str | None] = mapped_column(String(200), nullable=True)
    soil_preference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    growth_habit: Mapped[str | None] = mapped_column(String(200), nullable=True)
    edible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    indoor_friendly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    flowering: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    growth_range_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)
    growth_range_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    cover_asset = relationship("Asset", foreign_keys=[cover_asset_id], back_populates="plant_covers")
    growth_range_asset = relationship("Asset", foreign_keys=[growth_range_asset_id], back_populates="plant_growth_ranges")
    articles = relationship("Article", back_populates="plant")
    category_links = relationship("PlantCategory", back_populates="plant", cascade="all, delete-orphan")
    tag_links = relationship("PlantTag", back_populates="plant", cascade="all, delete-orphan")


class PlantCategory(Base):
    __tablename__ = "plant_categories"
    __table_args__ = (UniqueConstraint("plant_id", "category_id", name="uq_plant_categories_plant_category"),)

    plant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("plants.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    plant = relationship("Plant", back_populates="category_links")
    category = relationship("Category", back_populates="plant_links")


class PlantTag(Base):
    __tablename__ = "plant_tags"
    __table_args__ = (UniqueConstraint("plant_id", "tag_id", name="uq_plant_tags_plant_tag"),)

    plant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("plants.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    plant = relationship("Plant", back_populates="tag_links")
    tag = relationship("Tag", back_populates="plant_links")
