from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import status, HTTPException

from app.repositories.event import EventRepository

from app.schemas.event import EventResponse, EventUpdate
from app.schemas.user import UserBase


class EventService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.events = EventRepository(db)

    async def get_published_events(self) -> list[EventResponse]:
        db_events = await self.events.get_published()
        return [EventResponse.model_validate(event) for event in db_events]

    async def get_user_events(self, user: UserBase) -> list[EventResponse]:
        db_events = await self.events.get_user_events(user_id=user.id)
        return [EventResponse.model_validate(event) for event in db_events]

    async def get_all_events(self) -> list[EventResponse]:
        db_events = await self.events.get_all_events()
        return [EventResponse.model_validate(event) for event in db_events]

    async def update_by_id(self, id: int, data: EventUpdate) -> EventResponse:
        db_event = await self.events.get_by_id(event_id=id)
        
        if not db_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        update_data = data.model_dump(exclude_unset=True)

        new_event = await self.events.update(
            data=update_data,
            event=db_event
        )

        await self._db.commit()
        return EventResponse.model_validate(new_event)

    async def delete_by_id(self, *, id: int) -> None:
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
        
        await self.events.delete(event=db_event)
        await self._db.commit()