from sqlalchemy import ForeignKey, String, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from datetime import datetime


class ReviewReply(Base):
    __tablename__ = "review_reply"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id")
    )
    review_id: Mapped[int] = mapped_column(
        ForeignKey("review.id")
    )
    comment: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="review_replies", lazy="raise")
    review: Mapped["Review"] = relationship(back_populates="replies", lazy="raise")

    def __repr__(self) -> str:
        return f"<ReviewReply id={self.id} review_id={self.review_id}>"