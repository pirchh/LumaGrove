"""phase 6a schedules

Revision ID: 0003_phase6a_schedules
Revises: 0002_phase2_core_models
Create Date: 2026-04-23 21:15:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0003_phase6a_schedules"
down_revision = "0002_phase2_core_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schedules",
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("desired_state", sa.Boolean(), nullable=False),
        sa.Column("time_local", sa.Time(timezone=False), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column("rrule", sa.String(length=255), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("next_run_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_schedules_device_id"), "schedules", ["device_id"], unique=False)
    op.create_index(op.f("ix_schedules_next_run_at_utc"), "schedules", ["next_run_at_utc"], unique=False)
    op.create_index("ix_schedules_due_enabled", "schedules", ["is_enabled", "next_run_at_utc"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_schedules_due_enabled", table_name="schedules")
    op.drop_index(op.f("ix_schedules_next_run_at_utc"), table_name="schedules")
    op.drop_index(op.f("ix_schedules_device_id"), table_name="schedules")
    op.drop_table("schedules")
