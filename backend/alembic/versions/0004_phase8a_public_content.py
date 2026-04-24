"""phase 8a public content

Revision ID: 0004_phase8a_public_content
Revises: 0003_phase6a_schedules
Create Date: 2026-04-24
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_phase8a_public_content"
down_revision = "0003_phase6a_schedules"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=False)
    op.create_index(op.f("ix_categories_slug"), "categories", ["slug"], unique=False)

    op.create_table(
        "tags",
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_tags_name"), "tags", ["name"], unique=False)
    op.create_index(op.f("ix_tags_slug"), "tags", ["slug"], unique=False)

    op.create_table(
        "plants",
        sa.Column("common_name", sa.String(length=160), nullable=False),
        sa.Column("latin_name", sa.String(length=160), nullable=True),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("origin_region", sa.String(length=160), nullable=True),
        sa.Column("growth_zones", sa.String(length=160), nullable=True),
        sa.Column("light_preference", sa.String(length=200), nullable=True),
        sa.Column("water_preference", sa.String(length=200), nullable=True),
        sa.Column("humidity_preference", sa.String(length=200), nullable=True),
        sa.Column("temperature_range", sa.String(length=200), nullable=True),
        sa.Column("soil_preference", sa.String(length=200), nullable=True),
        sa.Column("growth_habit", sa.String(length=200), nullable=True),
        sa.Column("edible", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("indoor_friendly", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("flowering", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("cover_image_url", sa.Text(), nullable=True),
        sa.Column("growth_range_image_url", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_plants_common_name"), "plants", ["common_name"], unique=False)
    op.create_index(op.f("ix_plants_latin_name"), "plants", ["latin_name"], unique=False)
    op.create_index(op.f("ix_plants_slug"), "plants", ["slug"], unique=False)

    op.create_table(
        "articles",
        sa.Column("plant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("slug", sa.String(length=240), nullable=False),
        sa.Column("article_type", sa.String(length=40), server_default="article", nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("cover_image_url", sa.Text(), nullable=True),
        sa.Column("published_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("is_public", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_articles_article_type"), "articles", ["article_type"], unique=False)
    op.create_index(op.f("ix_articles_is_public"), "articles", ["is_public"], unique=False)
    op.create_index(op.f("ix_articles_plant_id"), "articles", ["plant_id"], unique=False)
    op.create_index(op.f("ix_articles_published_at_utc"), "articles", ["published_at_utc"], unique=False)
    op.create_index(op.f("ix_articles_slug"), "articles", ["slug"], unique=False)
    op.create_index(op.f("ix_articles_title"), "articles", ["title"], unique=False)

    op.create_table(
        "plant_categories",
        sa.Column("plant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("plant_id", "category_id"),
        sa.UniqueConstraint("plant_id", "category_id", name="uq_plant_categories_plant_category"),
    )
    op.create_table(
        "plant_tags",
        sa.Column("plant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("plant_id", "tag_id"),
        sa.UniqueConstraint("plant_id", "tag_id", name="uq_plant_tags_plant_tag"),
    )
    op.create_table(
        "article_sections",
        sa.Column("article_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("section_date", sa.Date(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("anchor_slug", sa.String(length=180), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("article_id", "anchor_slug", name="uq_article_sections_article_anchor"),
    )
    op.create_index(op.f("ix_article_sections_article_id"), "article_sections", ["article_id"], unique=False)
    op.create_index(op.f("ix_article_sections_section_date"), "article_sections", ["section_date"], unique=False)
    op.create_table(
        "article_categories",
        sa.Column("article_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id", "category_id"),
        sa.UniqueConstraint("article_id", "category_id", name="uq_article_categories_article_category"),
    )
    op.create_table(
        "article_tags",
        sa.Column("article_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id", "tag_id"),
        sa.UniqueConstraint("article_id", "tag_id", name="uq_article_tags_article_tag"),
    )


def downgrade() -> None:
    op.drop_table("article_tags")
    op.drop_table("article_categories")
    op.drop_index(op.f("ix_article_sections_section_date"), table_name="article_sections")
    op.drop_index(op.f("ix_article_sections_article_id"), table_name="article_sections")
    op.drop_table("article_sections")
    op.drop_table("plant_tags")
    op.drop_table("plant_categories")
    op.drop_index(op.f("ix_articles_title"), table_name="articles")
    op.drop_index(op.f("ix_articles_slug"), table_name="articles")
    op.drop_index(op.f("ix_articles_published_at_utc"), table_name="articles")
    op.drop_index(op.f("ix_articles_plant_id"), table_name="articles")
    op.drop_index(op.f("ix_articles_is_public"), table_name="articles")
    op.drop_index(op.f("ix_articles_article_type"), table_name="articles")
    op.drop_table("articles")
    op.drop_index(op.f("ix_plants_slug"), table_name="plants")
    op.drop_index(op.f("ix_plants_latin_name"), table_name="plants")
    op.drop_index(op.f("ix_plants_common_name"), table_name="plants")
    op.drop_table("plants")
    op.drop_index(op.f("ix_tags_slug"), table_name="tags")
    op.drop_index(op.f("ix_tags_name"), table_name="tags")
    op.drop_table("tags")
    op.drop_index(op.f("ix_categories_slug"), table_name="categories")
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_table("categories")
