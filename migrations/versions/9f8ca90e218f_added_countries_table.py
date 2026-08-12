"""Added Countries table

Revision ID: 9f8ca90e218f
Revises: 20260621_0155
Create Date: 2026-06-21 16:35:39.890265
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '9f8ca90e218f'
down_revision: str | None = '20260621_0155'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
