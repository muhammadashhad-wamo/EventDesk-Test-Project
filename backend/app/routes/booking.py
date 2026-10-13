from fastapi import APIRouter, status, BackgroundTasks

from app.core.dependencies import CurrentAdmin, CurrentUser, DbSession
from app.schemas.booking import BookingResponse, BookingCreate, BookingDetailResponse, MyBookingResponse
from app.services.booking import BookingService

from app.schemas.pagination import Page, Pagination

from app.core.dependencies import GetEditableEvent

router = APIRouter(tags=["bookings"])
admin_router = APIRouter(prefix="/admin", tags=["bookings", "admin"])


@router.get("/bookings/me", response_model=list[MyBookingResponse])
async def get_my_bookings(user: CurrentUser, db: DbSession):
    return await BookingService(db).get_my_bookings(user_id=user.id)

@router.post(
    "/events/{event_id}/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def book_tickets(event_id: int, data: BookingCreate, user: CurrentUser, db: DbSession, background_tasks: BackgroundTasks):
    return await BookingService(db).book(user_id=user.id, event_id=event_id, data=data, background=background_tasks)

@router.patch("/events/{event_id}/bookings/me/cancel", response_model=BookingResponse)
async def cancel_my_booking(event_id: int, user: CurrentUser, db: DbSession, background_tasks: BackgroundTasks):
    return await BookingService(db).cancel(actor_id=user.id, actor_role=user.role, user_id=user.id, event_id=event_id, background=background_tasks)

@router.get("/events/{event_id}/bookings", response_model=Page[BookingDetailResponse])
async def get_event_bookings(
    event: GetEditableEvent,
    db: DbSession,
    pagination: Pagination,
    is_active: bool | None = None,
):
    return await BookingService(db).list_bookings(
        event_id=event.id, is_active=is_active, pagination=pagination
    )


######### Admin routes ###############

@admin_router.patch(
    "/events/{event_id}/bookings/{user_id}/cancel",
    response_model=BookingResponse,
)
async def admin_cancel_booking(event_id: int, user_id: int, current_admin: CurrentAdmin, db: DbSession, background_tasks: BackgroundTasks):
    return await BookingService(db).cancel(actor_id=current_admin.id, user_id=user_id, event_id=event_id, background=background_tasks)

@admin_router.get("/bookings", response_model=Page[BookingDetailResponse])
async def admin_get_all_bookings(
    current_admin: CurrentAdmin,
    db: DbSession,
    pagination: Pagination,
    event_id: int | None = None,
    user_id: int | None = None,
    is_active: bool | None = None,
):
    return await BookingService(db).list_bookings(
        event_id=event_id, user_id=user_id, is_active=is_active, pagination=pagination
    )