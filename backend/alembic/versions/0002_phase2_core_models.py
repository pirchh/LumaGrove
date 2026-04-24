"""phase 2 core models

Revision ID: 0002_phase2_core_models
Revises: 0001_initial_baseline
Create Date: 2026-04-23 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_phase2_core_models"
down_revision = "0001_initial_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "locations",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_locations_slug"), "locations", ["slug"], unique=False)

    op.create_table(
        "devices",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("device_type", sa.String(length=80), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_devices_device_type"), "devices", ["device_type"], unique=False)
    op.create_index(op.f("ix_devices_location_id"), "devices", ["location_id"], unique=False)

    op.create_table(
        "event_logs",
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("severity", sa.String(length=20), server_default=sa.text("'info'"), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_event_logs_created_at_utc"), "event_logs", ["created_at_utc"], unique=False)
    op.create_index(op.f("ix_event_logs_event_type"), "event_logs", ["event_type"], unique=False)
    op.create_index(op.f("ix_event_logs_severity"), "event_logs", ["severity"], unique=False)
    op.create_index(op.f("ix_event_logs_target_id"), "event_logs", ["target_id"], unique=False)
    op.create_index(op.f("ix_event_logs_target_type"), "event_logs", ["target_type"], unique=False)

    op.create_table(
        "device_state_cache",
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("last_seen_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("device_id"),
    )


def downgrade() -> None:
    op.drop_table("device_state_cache")
    op.drop_index(op.f("ix_event_logs_target_type"), table_name="event_logs")
    op.drop_index(op.f("ix_event_logs_target_id"), table_name="event_logs")
    op.drop_index(op.f("ix_event_logs_severity"), table_name="event_logs")
    op.drop_index(op.f("ix_event_logs_event_type"), table_name="event_logs")
    op.drop_index(op.f("ix_event_logs_created_at_utc"), table_name="event_logs")
    op.drop_table("event_logs")
    op.drop_index(op.f("ix_devices_location_id"), table_name="devices")
    op.drop_index(op.f("ix_devices_device_type"), table_name="devices")
    op.drop_table("devices")
    op.drop_index(op.f("ix_locations_slug"), table_name="locations")
    op.drop_table("locations")
