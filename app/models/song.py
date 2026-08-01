import enum

from sqlalchemy import BigInteger, CheckConstraint, Enum, ForeignKey, Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Vocal(str, enum.Enum):
    MALE = "Мужской"
    FEMALE = "Женский"
    MIX = "Смешанный"


class Song(Base):
    __tablename__ = "songs"
    __table_args__ = (
        CheckConstraint("energy BETWEEN 0 AND 100", name="energy_range"),
        CheckConstraint("danceability BETWEEN 0 AND 100", name="danceability_range"),
        CheckConstraint("happiness BETWEEN 0 AND 100", name="happiness_range"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    country_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("countries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    artist: Mapped[str] = mapped_column(String(255), nullable=False)
    bpm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    key: Mapped[str | None] = mapped_column(String(16), nullable=True)
    vocal: Mapped[Vocal] = mapped_column(
        Enum(Vocal, name="vocal", native_enum=True, values_callable=lambda x: [e.value for e in x]), nullable=False)
    energy: Mapped[int | None] = mapped_column(Integer, nullable=True)
    danceability: Mapped[int | None] = mapped_column(Integer, nullable=True)
    happiness: Mapped[int | None] = mapped_column(Integer, nullable=True)
    url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    country: Mapped["Country"] = relationship(back_populates="songs")
