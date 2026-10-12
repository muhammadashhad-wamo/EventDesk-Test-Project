from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    events: Mapped[list["Event"]] = relationship(
        back_populates="category", lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"