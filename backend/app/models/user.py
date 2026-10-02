from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    organized_events: Mapped[list["Event"]] = relationship(
        back_populates="organizer", lazy="raise"
    )
    bookings: Mapped[list["EventBooking"]] = relationship(
        back_populates="user", lazy="raise"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="user", lazy="raise"
    )
    review_replies: Mapped[list["ReviewReply"]] = relationship(
        back_populates="user", lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"