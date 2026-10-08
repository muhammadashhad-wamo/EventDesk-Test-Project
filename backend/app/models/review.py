from sqlalchemy import ForeignKey, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from datetime import datetime


class Review(Base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id")
    )
    event_id: Mapped[int] = mapped_column(
        ForeignKey("event.id")
    )
    stars_count: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="reviews", lazy="raise")
    event: Mapped["Event"] = relationship(back_populates="reviews", lazy="joined")
    replies: Mapped[list["ReviewReply"]] = relationship(
        back_populates="review", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Review id={self.id} event_id={self.event_id} stars={self.stars_count}>"