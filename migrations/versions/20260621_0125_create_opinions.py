"""create opinions

Revision ID: 20260621_0125
Revises:
Create Date: 2026-06-21 01:25:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260621_0125"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The enum is created explicitly below.  Disable SQLAlchemy's automatic
    # creation during ``create_table`` to avoid issuing CREATE TYPE twice.
    stage = postgresql.ENUM("FIRST", "FINAL", name="stage", create_type=False)
    stage.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "opinions",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("song_id", sa.BigInteger(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("stage", stage, nullable=False),
        sa.CheckConstraint(
            "score IN (0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12)",
            name=op.f("ck_opinions_score_allowed"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_opinions")),
    )
    op.create_index(op.f("ix_opinions_song_id"), "opinions", ["song_id"], unique=False)
    op.create_index(op.f("ix_opinions_user_id"), "opinions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_opinions_user_id"), table_name="opinions")
    op.drop_index(op.f("ix_opinions_song_id"), table_name="opinions")
    op.drop_table("opinions")
    sa.Enum(name="stage").drop(op.get_bind(), checkfirst=True)
