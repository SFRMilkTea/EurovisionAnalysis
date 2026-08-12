from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SongLanguage(Base):
    __tablename__ = "song_languages"

    song_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("songs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    language_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("languages.id", ondelete="CASCADE"),
        primary_key=True,
    )

