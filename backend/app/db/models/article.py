from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Article(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "articles"

    plant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("plants.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(220), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(240), nullable=False, unique=True, index=True)
    article_type: Mapped[str] = mapped_column(String(40), nullable=False, default="article", server_default="article", index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)
    published_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true", index=True)

    plant = relationship("Plant", back_populates="articles")
    cover_asset = relationship("Asset", foreign_keys=[cover_asset_id], back_populates="article_covers")
    sections = relationship("ArticleSection", back_populates="article", cascade="all, delete-orphan", order_by="ArticleSection.sort_order")
    category_links = relationship("ArticleCategory", back_populates="article", cascade="all, delete-orphan")
    tag_links = relationship("ArticleTag", back_populates="article", cascade="all, delete-orphan")


class ArticleSection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "article_sections"
    __table_args__ = (UniqueConstraint("article_id", "anchor_slug", name="uq_article_sections_article_anchor"),)

    article_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    section_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    anchor_slug: Mapped[str] = mapped_column(String(180), nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)

    article = relationship("Article", back_populates="sections")
    asset = relationship("Asset", foreign_keys=[asset_id], back_populates="article_sections")


class ArticleCategory(Base):
    __tablename__ = "article_categories"
    __table_args__ = (UniqueConstraint("article_id", "category_id", name="uq_article_categories_article_category"),)

    article_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    article = relationship("Article", back_populates="category_links")
    category = relationship("Category", back_populates="article_links")


class ArticleTag(Base):
    __tablename__ = "article_tags"
    __table_args__ = (UniqueConstraint("article_id", "tag_id", name="uq_article_tags_article_tag"),)

    article_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    article = relationship("Article", back_populates="tag_links")
    tag = relationship("Tag", back_populates="article_links")
