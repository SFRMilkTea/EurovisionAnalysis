import enum

from sqlalchemy import BigInteger, CheckConstraint, Enum, ForeignKey, Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Stage(str, enum.Enum):
    FIRST = "FIRST"
    FINAL = "FINAL"


class Opinion(Base):
    __tablename__ = "opinions"
    __table_args__ = (
        CheckConstraint("score IN (0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12)", name="score_allowed"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    song_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("songs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    stage: Mapped[Stage] = mapped_column(
        Enum(Stage, name="stage", native_enum=True),
        nullable=False,
    )
