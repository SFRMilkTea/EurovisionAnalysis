"""Create events and link songs

Revision ID: 20260812_2000
Revises: 2114b3b48d4e
Create Date: 2026-08-12 20:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260812_2000"
down_revision: str | None = "2114b3b48d4e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("host", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
    )
    op.create_index(op.f("ix_events_year"), "events", ["year"], unique=False)

    op.add_column("songs", sa.Column("event_id", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_songs_event_id"), "songs", ["event_id"], unique=False)
    op.create_foreign_key(
        op.f("fk_songs_event_id_events"),
        "songs",
        "events",
        ["event_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("fk_songs_event_id_events"), "songs", type_="foreignkey")
    op.drop_index(op.f("ix_songs_event_id"), table_name="songs")
    op.drop_column("songs", "event_id")
    op.drop_index(op.f("ix_events_year"), table_name="events")
    op.drop_table("events")
