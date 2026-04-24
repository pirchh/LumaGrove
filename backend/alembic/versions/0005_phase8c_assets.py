"""phase 8c assets and media uploads

Revision ID: 0005_phase8c_assets
Revises: 0004_phase8a_public_content
Create Date: 2026-04-24
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_phase8c_assets"
down_revision = "0004_phase8a_public_content"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("original_filename", sa.String(length=260), nullable=False),
        sa.Column("stored_filename", sa.String(length=320), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("public_url", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sha256", name="uq_assets_sha256"),
        sa.UniqueConstraint("stored_filename"),
    )
    op.create_index(op.f("ix_assets_sha256"), "assets", ["sha256"], unique=False)

    op.add_column("plants", sa.Column("cover_asset_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("plants", sa.Column("growth_range_asset_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f("ix_plants_cover_asset_id"), "plants", ["cover_asset_id"], unique=False)
    op.create_index(op.f("ix_plants_growth_range_asset_id"), "plants", ["growth_range_asset_id"], unique=False)
    op.create_foreign_key("fk_plants_cover_asset_id_assets", "plants", "assets", ["cover_asset_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_plants_growth_range_asset_id_assets", "plants", "assets", ["growth_range_asset_id"], ["id"], ondelete="SET NULL")

    op.add_column("articles", sa.Column("cover_asset_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f("ix_articles_cover_asset_id"), "articles", ["cover_asset_id"], unique=False)
    op.create_foreign_key("fk_articles_cover_asset_id_assets", "articles", "assets", ["cover_asset_id"], ["id"], ondelete="SET NULL")

    op.add_column("article_sections", sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f("ix_article_sections_asset_id"), "article_sections", ["asset_id"], unique=False)
    op.create_foreign_key("fk_article_sections_asset_id_assets", "article_sections", "assets", ["asset_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    op.drop_constraint("fk_article_sections_asset_id_assets", "article_sections", type_="foreignkey")
    op.drop_index(op.f("ix_article_sections_asset_id"), table_name="article_sections")
    op.drop_column("article_sections", "asset_id")

    op.drop_constraint("fk_articles_cover_asset_id_assets", "articles", type_="foreignkey")
    op.drop_index(op.f("ix_articles_cover_asset_id"), table_name="articles")
    op.drop_column("articles", "cover_asset_id")

    op.drop_constraint("fk_plants_growth_range_asset_id_assets", "plants", type_="foreignkey")
    op.drop_constraint("fk_plants_cover_asset_id_assets", "plants", type_="foreignkey")
    op.drop_index(op.f("ix_plants_growth_range_asset_id"), table_name="plants")
    op.drop_index(op.f("ix_plants_cover_asset_id"), table_name="plants")
    op.drop_column("plants", "growth_range_asset_id")
    op.drop_column("plants", "cover_asset_id")

    op.drop_index(op.f("ix_assets_sha256"), table_name="assets")
    op.drop_table("assets")
