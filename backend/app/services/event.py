from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, AuditEntity, EventStatus
from app.models.tag import Tag
from app.models.venue import Venue
from app.models.category import Category
from app.repositories.audit_log import AuditLogRepository
from app.repositories.event import EventRepository
from app.repositories.tag import TagRepository
from app.repositories.venue import VenueRepository
from app.repositories.category import CategoryRepository
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.schemas.event_filters import EventFilters
from app.schemas.pagination import Page, PaginationParams
from app.schemas.user import UserBase
from app.tasks.notifications import event_cancelled


class EventService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.events = EventRepository(db)
        self.venues = VenueRepository(db)
        self.tags = TagRepository(db)
        self.audit = AuditLogRepository(db)
        self.categories = CategoryRepository(db)

    async def list_events(
        self,
        *,
        filters: EventFilters,
        pagination: PaginationParams,
        published_only: bool = False,
        organizer_id: int | None = None,
        status: EventStatus | None = None,
        get_deleted: bool = False,
    ) -> Page[EventResponse]:
        db_events, total = await self.events.search(
            filters=filters,
            limit=pagination.limit,
            offset=pagination.offset,
            published_only=published_only,
            organizer_id=organizer_id,
            status=status,
            get_deleted=get_deleted,
        )
        return Page[EventResponse](
            items=[EventResponse.model_validate(event) for event in db_events],
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    async def create(self, user: UserBase, data: EventCreate) -> EventResponse:
        venue = await self._get_venue(data.venue_id) if data.venue_id is not None else None
        category = await self._get_category(data.category_id) if data.category_id is not None else None
        tags = await self._get_tags(data.tag_ids)

        try:
            db_event = await self.events.create(
                organizer_id=user.id,
                time=data.time,
                title=data.title,
                description=data.description,
                status=data.status,
                category=category,
                ticket_price=data.ticket_price,
                available_tickets_count=data.available_tickets_count,
                venue=venue,
                tags=tags,
                is_active=True,
            )
            await self.audit.create(
                actor_id=user.id,
                action=AuditAction.EVENT_CREATED,
                entity_type=AuditEntity.EVENT,
                entity_id=db_event.id,
            )
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        return EventResponse.model_validate(db_event)

    async def update_by_id(self, id: int, data: EventUpdate, actor: UserBase) -> EventResponse:
        return await self._update_and_audit(
            id=id, data=data, actor=actor, action=AuditAction.EVENT_UPDATED
        )

    async def cancel_event_by_id(self, id: int, actor: UserBase, background: BackgroundTasks) -> EventResponse:
        db_event = await self.events.get_by_id(event_id=id)

        if not db_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        if db_event.status in (EventStatus.CANCELLED.value, EventStatus.COMPLETED.value):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Event is already {db_event.status}"
            )

        response = await self._update_and_audit(
            id=id,
            data=EventUpdate(status=EventStatus.CANCELLED),
            actor=actor,
            action=AuditAction.EVENT_CANCELLED,
        )
        background.add_task(event_cancelled, event_id=id)
        return response

    async def delete_by_id(self, *, id: int, actor: UserBase) -> None:
        db_event = await self.events.get_by_id(event_id=id, get_deleted=True)

        if not db_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        if not db_event.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Event is already deleted"
            )

        try:
            await self.events.delete(event=db_event)
            await self.audit.create(
                actor_id=actor.id,
                action=AuditAction.EVENT_DELETED,
                entity_type=AuditEntity.EVENT,
                entity_id=db_event.id,
            )
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

    async def _update_and_audit(
        self,
        *,
        id: int,
        data: EventUpdate,
        actor: UserBase,
        action: AuditAction,
    ) -> EventResponse:
        db_event = await self.events.get_by_id(event_id=id)

        if not db_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        update_data = data.model_dump(exclude_unset=True)

        tag_ids = update_data.pop("tag_ids", None)
        tags = await self._get_tags(tag_ids) if tag_ids is not None else None

        set_venue = "venue_id" in update_data
        venue_id = update_data.pop("venue_id", None)
        venue = await self._get_venue(venue_id) if venue_id is not None else None
        set_category = "category_id" in update_data
        category_id = update_data.pop("category_id", None)
        category = await self._get_category(category_id) if category_id is not None else None

        try:
            updated_event = await self.events.update(
                event=db_event,
                data=update_data,
                venue=venue,
                set_venue=set_venue,
                tags=tags,
                category=category,
                set_category=set_category,
            )
            await self.audit.create(
                actor_id=actor.id,
                action=action,
                entity_type=AuditEntity.EVENT,
                entity_id=updated_event.id,
            )
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        return EventResponse.model_validate(updated_event)

    async def _get_venue(self, venue_id: int) -> Venue:
        venue = await self.venues.get_by_id(venue_id)
        if venue is None:
            raise HTTPException(status_code=422, detail="Venue not found")
        return venue

    async def _get_tags(self, tag_ids: list[int]) -> list[Tag]:
        unique_ids = list(dict.fromkeys(tag_ids))
        tags = await self.tags.get_by_ids(unique_ids)
        missing = set(unique_ids) - {tag.id for tag in tags}
        if missing:
            raise HTTPException(status_code=422, detail=f"Unknown tag ids: {sorted(missing)}")
        return tags

    async def _get_category(self, category_id: int) -> Category:
        category = await self.categories.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=422, detail="Category not found")
        return category