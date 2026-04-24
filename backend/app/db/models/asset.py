from __future__ import annotations

from sqlalchemy import BigInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Asset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint("sha256", name="uq_assets_sha256"),)

    original_filename: Mapped[str] = mapped_column(String(260), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    public_url: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    plant_covers = relationship("Plant", foreign_keys="Plant.cover_asset_id", back_populates="cover_asset")
    plant_growth_ranges = relationship("Plant", foreign_keys="Plant.growth_range_asset_id", back_populates="growth_range_asset")
    article_covers = relationship("Article", foreign_keys="Article.cover_asset_id", back_populates="cover_asset")
    article_sections = relationship("ArticleSection", foreign_keys="ArticleSection.asset_id", back_populates="asset")
