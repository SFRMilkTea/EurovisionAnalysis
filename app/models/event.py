from typing import List

from sqlalchemy import BigInteger, Boolean, Identity, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    first_stage_open: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    final_stage_open: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    host_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("countries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    host: Mapped["Country"] = relationship(back_populates="events")
    songs: Mapped[List["Song"]] = relationship(back_populates="event")
