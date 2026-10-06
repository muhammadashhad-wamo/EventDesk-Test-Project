from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, Integer, func, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from datetime import datetime



class EventBooking(Base):
    __tablename__ = "event_booking"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id"),
        primary_key=True,
    )
    event_id: Mapped[int] = mapped_column(
        ForeignKey("event.id"),
        primary_key=True,
    )
    tickets_count: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_booking: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship(back_populates="bookings", lazy="raise")
    event: Mapped["Event"] = relationship(back_populates="bookings", lazy="raise")

    def __repr__(self) -> str:
        return (
            f"<EventBooking user_id={self.user_id} event_id={self.event_id} "
            f"tickets={self.tickets_count}>"
        )