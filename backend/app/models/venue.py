from sqlalchemy import String, Boolean, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Venue(Base):
    __tablename__ = "venue"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    street: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
            Index(
                "uq_venue_normalized_address",
                func.lower(func.btrim(title)),
                func.lower(func.btrim(street)),
                func.lower(func.btrim(city)),
                func.lower(func.btrim(country)),
                unique=True,
            ),
        )

    events: Mapped[list["Event"]] = relationship(
        back_populates="venue", lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<Venue id={self.id} title={self.title!r}>"