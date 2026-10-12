from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import Depends, Query


def _as_utc(value: datetime | None) -> datetime | None:
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


class EventFilters:
    def __init__(
        self,
        search: str | None = Query(None, min_length=1, max_length=100, description="Matches title or description"),
        category: str | None = Query(None, max_length=50),
        venue_id: int | None = None,
        city: str | None = Query(None, max_length=50, description="City of the event's venue"),
        tags: list[str] | None = Query(None, description="Events having ANY of these tags"),
        min_price: Decimal | None = Query(None, ge=0),
        max_price: Decimal | None = Query(None, ge=0),
        starts_after: datetime | None = None,
        starts_before: datetime | None = None,
        has_tickets: bool | None = Query(None, description="true: tickets left, false: sold out"),
        sort_by: Literal["time", "price", "title"] = "time",
        order: Literal["asc", "desc"] = "asc",
    ) -> None:
        self.search = search
        self.category = category
        self.venue_id = venue_id
        self.city = city
        self.tags = tags
        self.min_price = min_price
        self.max_price = max_price
        self.starts_after = _as_utc(starts_after)
        self.starts_before = _as_utc(starts_before)
        self.has_tickets = has_tickets
        self.sort_by = sort_by
        self.order = order


EventFilterParams = Annotated[EventFilters, Depends()]