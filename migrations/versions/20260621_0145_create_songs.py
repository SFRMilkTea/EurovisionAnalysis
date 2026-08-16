"""create songs

Revision ID: 20260621_0145
Revises: 20260621_0135
Create Date: 2026-06-21 01:45:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260621_0145"
down_revision: str | None = "20260621_0135"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The enum is created explicitly below.  Disable automatic creation while
    # creating the table, otherwise PostgreSQL receives CREATE TYPE twice.
    vocal = postgresql.ENUM("male", "female", "mix", name="vocal", create_type=False)
    vocal.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "genres",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_genres")),
    )
    op.create_index(op.f("ix_genres_name"), "genres", ["name"], unique=True)

    op.create_table(
        "languages",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_languages")),
    )
    op.create_index(op.f("ix_languages_name"), "languages", ["name"], unique=True)

    op.create_table(
        "songs",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("country_id", sa.BigInteger(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("artist", sa.String(length=255), nullable=False),
        sa.Column("bpm", sa.Integer(), nullable=True),
        sa.Column("key", sa.String(length=16), nullable=True),
        sa.Column("vocal", vocal, nullable=False),
        sa.Column("energy", sa.Integer(), nullable=True),
        sa.Column("danceability", sa.Integer(), nullable=True),
        sa.Column("happiness", sa.Integer(), nullable=True),
        sa.CheckConstraint("energy BETWEEN 0 AND 100", name=op.f("ck_songs_energy_range")),
        sa.CheckConstraint(
            "danceability BETWEEN 0 AND 100",
            name=op.f("ck_songs_danceability_range"),
        ),
        sa.CheckConstraint(
            "happiness BETWEEN 0 AND 100",
            name=op.f("ck_songs_happiness_range"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_songs")),
    )
    op.create_index(op.f("ix_songs_country_id"), "songs", ["country_id"], unique=False)
    op.create_index(op.f("ix_songs_year"), "songs", ["year"], unique=False)

    op.create_table(
        "song_genres",
        sa.Column("song_id", sa.BigInteger(), nullable=False),
        sa.Column("genre_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["genre_id"],
            ["genres.id"],
            name=op.f("fk_song_genres_genre_id_genres"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["song_id"],
            ["songs.id"],
            name=op.f("fk_song_genres_song_id_songs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("song_id", "genre_id", name=op.f("pk_song_genres")),
    )

    op.create_table(
        "song_languages",
        sa.Column("song_id", sa.BigInteger(), nullable=False),
        sa.Column("language_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["language_id"],
            ["languages.id"],
            name=op.f("fk_song_languages_language_id_languages"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["song_id"],
            ["songs.id"],
            name=op.f("fk_song_languages_song_id_songs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("song_id", "language_id", name=op.f("pk_song_languages")),
    )

    op.create_foreign_key(
        op.f("fk_opinions_song_id_songs"),
        "opinions",
        "songs",
        ["song_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("fk_opinions_song_id_songs"), "opinions", type_="foreignkey")
    op.drop_table("song_languages")
    op.drop_table("song_genres")
    op.drop_index(op.f("ix_songs_year"), table_name="songs")
    op.drop_index(op.f("ix_songs_country_id"), table_name="songs")
    op.drop_table("songs")
    op.drop_index(op.f("ix_languages_name"), table_name="languages")
    op.drop_table("languages")
    op.drop_index(op.f("ix_genres_name"), table_name="genres")
    op.drop_table("genres")
    sa.Enum(name="vocal").drop(op.get_bind(), checkfirst=True)
