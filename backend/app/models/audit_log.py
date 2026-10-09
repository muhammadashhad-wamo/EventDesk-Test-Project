from sqlalchemy import ForeignKey, String, Integer, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from datetime import datetime


class AuditLog(Base):

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_account.id")
    )
    action: Mapped[str] = mapped_column(String(50))
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    actor: Mapped["User | None"] = relationship(lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<AuditLog id={self.id} actor_id={self.actor_id} "
            f"{self.action} {self.entity_type}:{self.entity_id}>"
        )