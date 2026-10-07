from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.tag import event_tag


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    organizer_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id")
    )
    venue_id: Mapped[int | None] = mapped_column(
        ForeignKey("venue.id")
    )
    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))
    ticket_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    available_tickets_count: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    organizer: Mapped["User"] = relationship(
        back_populates="organized_events", lazy="raise"
    )
    venue: Mapped["Venue"] = relationship(back_populates="events", lazy="raise")
    bookings: Mapped[list["EventBooking"]] = relationship(
        back_populates="event", lazy="raise"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="event", lazy="raise"
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary=event_tag, back_populates="events", lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<Event id={self.id} title={self.title!r} status={self.status}>"