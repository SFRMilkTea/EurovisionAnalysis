"""Fix vocal manually

Revision ID: 2114b3b48d4e
Revises: 598e6173bb2b
Create Date: 2026-06-21 18:07:51.814126
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '2114b3b48d4e'
down_revision: str | None = '598e6173bb2b'
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
