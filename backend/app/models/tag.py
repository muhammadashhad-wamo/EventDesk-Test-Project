from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

event_tag = Table(
    "event_tag",
    Base.metadata,
    Column(
        "event_id",
        Integer,
        ForeignKey("event.id"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tag.id"),
        primary_key=True
    ),
)


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(50), unique=True)

    events: Mapped[list["Event"]] = relationship(
        secondary=event_tag, back_populates="tags", lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<Tag id={self.id} tag={self.tag!r}>"