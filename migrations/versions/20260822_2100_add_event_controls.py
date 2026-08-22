"""Add current-event and voting-stage controls."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260822_2100"
down_revision: str | None = "d18090a6c68a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("events", sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("events", sa.Column("first_stage_open", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.add_column("events", sa.Column("final_stage_open", sa.Boolean(), nullable=False, server_default=sa.text("true")))


def downgrade() -> None:
    op.drop_column("events", "final_stage_open")
    op.drop_column("events", "first_stage_open")
    op.drop_column("events", "is_current")
