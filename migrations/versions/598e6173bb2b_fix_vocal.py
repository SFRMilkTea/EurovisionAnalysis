"""Fix vocal

Revision ID: 598e6173bb2b
Revises: 20260621_0205
Create Date: 2026-06-21 17:57:25.016493
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '598e6173bb2b'
down_revision: str | None = '20260621_0205'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    op.execute("CREATE TYPE vocal_new AS ENUM ('Мужской', 'Женский', 'Смешанный')")

    op.execute("""
        ALTER TABLE songs 
        ALTER COLUMN vocal TYPE vocal_new 
        USING vocal::text::vocal_new
    """)

    op.execute("DROP TYPE vocal")

    # 4. Переименовываем новый тип в 'vocal'
    op.execute("ALTER TYPE vocal_new RENAME TO vocal")


def downgrade():
    op.execute("CREATE TYPE vocal_old AS ENUM ('MALE', 'FEMALE', 'MIX')")
    op.execute("""
        ALTER TABLE songs 
        ALTER COLUMN vocal TYPE vocal_old 
        USING vocal::text::vocal_old
    """)
    op.execute("DROP TYPE vocal")
    op.execute("ALTER TYPE vocal_old RENAME TO vocal")