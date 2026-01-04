"""init

Revision ID: 0001
Revises: 
Create Date: 2026-01-04 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "metric",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("voltage", sa.Float(), nullable=False),
        sa.Column("current", sa.Float(), nullable=False),
        sa.Column("power", sa.Float(), nullable=False),
        sa.Column("flow_rate", sa.Float(), nullable=False),
        sa.Column("spindle_temp", sa.Float(), nullable=False),
        sa.Column("vibration_rms", sa.Float(), nullable=False),
        sa.Column("vibration_x_rms", sa.Float(), nullable=True),
        sa.Column("vibration_y_rms", sa.Float(), nullable=True),
        sa.Column("vibration_z_rms", sa.Float(), nullable=True),
        sa.Column("motor_current", sa.Float(), nullable=True),
        sa.Column("ground_present", sa.Boolean(), nullable=False),
        sa.Column("cycle_count", sa.Integer(), nullable=False),
    )
    op.create_table(
        "event",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )
    op.create_table(
        "maintenance",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("maintenance_type", sa.String(), nullable=False),
        sa.Column("performed_by", sa.String(), nullable=False),
        sa.Column("comment", sa.String(), nullable=True),
    )
    op.create_table(
        "threshold",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vibration_warn", sa.Float(), nullable=False),
        sa.Column("vibration_alarm", sa.Float(), nullable=False),
        sa.Column("vibration_reset", sa.Float(), nullable=False),
        sa.Column("spindle_temp_warn", sa.Float(), nullable=False),
        sa.Column("spindle_temp_alarm", sa.Float(), nullable=False),
        sa.Column("spindle_temp_reset", sa.Float(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("threshold")
    op.drop_table("maintenance")
    op.drop_table("event")
    op.drop_table("metric")
