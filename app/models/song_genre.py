from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SongGenre(Base):
    __tablename__ = "song_genres"

    song_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("songs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    genre_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    )

