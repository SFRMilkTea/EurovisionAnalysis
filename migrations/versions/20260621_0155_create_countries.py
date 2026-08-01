"""create countries

Revision ID: 20260621_0155
Revises: 20260621_0145
Create Date: 2026-06-21 01:55:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260621_0155"
down_revision: str | None = "20260621_0145"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "countries",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_countries")),
    )
    op.create_index(op.f("ix_countries_name"), "countries", ["name"], unique=True)
    op.create_foreign_key(
        op.f("fk_songs_country_id_countries"),
        "songs",
        "countries",
        ["country_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("fk_songs_country_id_countries"), "songs", type_="foreignkey")
    op.drop_index(op.f("ix_countries_name"), table_name="countries")
    op.drop_table("countries")
