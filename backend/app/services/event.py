from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import status, HTTPException, BackgroundTasks

from app.repositories.audit_log import AuditLogRepository
from app.repositories.event import EventRepository

from app.schemas.event import EventResponse, EventUpdate, EventCreate
from app.schemas.user import UserBase

from app.core.enums import EventStatus, AuditAction, AuditEntity

from app.tasks.notifications import event_cancelled


class EventService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.events = EventRepository(db)
        self.audit = AuditLogRepository(db)

    async def get_published_events(self, get_deleted: bool = False) -> list[EventResponse]:
        db_events = await self.events.get_published(get_deleted=get_deleted)
        return [EventResponse.model_validate(event) for event in db_events]

    async def get_user_events(self, user: UserBase, get_deleted: bool = False) -> list[EventResponse]:
        db_events = await self.events.get_user_events(user_id=user.id, get_deleted=get_deleted)
        return [EventResponse.model_validate(event) for event in db_events]

    async def get_all_events(self, get_deleted: bool = False) -> list[EventResponse]:
        db_events = await self.events.get_all_events(get_deleted=get_deleted)
        return [EventResponse.model_validate(event) for event in db_events]

    async def create(self, user: UserBase, data: EventCreate):
        try:
            db_event = await self.events.create(
                organizer_id=user.id,
                time=data.time,
                title=data.title,
                description=data.description,
                status=data.status,
                category=data.category,
                ticket_price=data.ticket_price,
                available_tickets_count=data.available_tickets_count,
                is_active=True,
            )
            await self.audit.create(
                actor_id=user.id,
                action=AuditAction.EVENT_CREATED,
                entity_type=AuditEntity.EVENT,
                entity_id=db_event.id,
            )
            await self._db.commit()
        except:
            await self._db.rollback()
            raise

        event_schema = EventResponse.model_validate(db_event)
        return event_schema

    async def update_by_id(self, id: int, data: EventUpdate, actor: UserBase) -> EventResponse:
        db_event = await self.events.get_by_id(event_id=id)
        
        if not db_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        try:
            update_data = data.model_dump(exclude_unset=True)
            new_event = await self.events.update(
                data=update_data,
                event=db_event
            )
            await self.audit.create(
                actor_id=actor.id,
                action=AuditAction.EVENT_UPDATED,
                entity_type=AuditEntity.EVENT,
                entity_id=new_event.id,
            )
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        return EventResponse.model_validate(new_event)

    async def cancel_event_by_id(self, id: int, background: BackgroundTasks, actor: UserBase) -> EventResponse:
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
        try:
            new_event = await self.events.update(
                data=EventUpdate(status=EventStatus.CANCELLED),
                event=db_event
            )
            await self.audit.create(
                actor_id=actor.id,
                action=AuditAction.EVENT_UPDATED,
                entity_type=AuditEntity.EVENT,
                entity_id=new_event.id,
            )
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        background.add_task(event_cancelled, event_id=id)

        return EventResponse.model_validate(new_event)

    async def delete_by_id(self, *, id: int, actor: UserBase) -> None:
        db_event = await self.events.get_by_id(event_id=id)
                
        if not db_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        if db_event.is_active == False:
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