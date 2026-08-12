from typing import List

from sqlalchemy import BigInteger, Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    host: Mapped[str] = mapped_column(String(255), nullable=False)

    songs: Mapped[List["Song"]] = relationship(back_populates="event")
