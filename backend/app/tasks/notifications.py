import asyncio
import logging

from app.core.enums import NotificationType
from app.db.session import AsyncSessionLocal
from app.models.notification import Notification
from app.realtime.manager import manager
from app.repositories.event import EventRepository
from app.repositories.notification import NotificationRepository
from app.repositories.user import UserRepository
from app.schemas.notification import NotificationCreate, NotificationResponse

logger = logging.getLogger(__name__)


def to_payloads(notifications: list[Notification]) -> list[tuple[int, dict]]:
    return [
        (
            n.user_id,
            {
                "type": "notification",
                "notification": NotificationResponse.model_validate(n).model_dump(mode="json"),
            },
        )
        for n in notifications
    ]


async def push(payloads: list[tuple[int, dict]]) -> None:
    await asyncio.gather(*(manager.send_to_user(uid, msg) for uid, msg in payloads))


async def deliver(items: list[NotificationCreate]) -> None:
    if not items:
        return
    try:
        async with AsyncSessionLocal() as db:
            db_notifications = await NotificationRepository(db).create_many(items)
            payloads = to_payloads(db_notifications)
            await db.commit()
    except Exception:
        logger.exception("Could not store notifications")
        return
    await push(payloads)


async def booking_confirmed(*, user_id: int, event_id: int, event_title: str, tickets_count: int) -> None:
    await deliver([NotificationCreate(
        user_id=user_id,
        type=NotificationType.BOOKING_CONFIRMED,
        message=f"Your booking for '{event_title}' is confirmed ({tickets_count} ticket(s)).",
        event_id=event_id,
    )])


async def booking_cancelled(*, user_id: int, event_id: int, event_title: str) -> None:
    await deliver([NotificationCreate(
        user_id=user_id,
        type=NotificationType.BOOKING_CANCELLED,
        message=f"Your booking for '{event_title}' was cancelled.",
        event_id=event_id,
    )])


async def event_cancelled(*, event_id: int) -> None:
    try:
        async with AsyncSessionLocal() as db:
            event = await EventRepository(db).get_by_id_with_bookings(event_id)
            if event is None:
                return
            items = [
                NotificationCreate(
                    user_id=booking.user_id,
                    type=NotificationType.EVENT_CANCELLED,
                    message=f"The event '{event.title}' was cancelled.",
                    event_id=event.id,
                )
                for booking in event.bookings
                if booking.is_active
            ]
    except Exception:
        logger.exception("Could not load attendees for event %s", event_id)
        return
    await deliver(items)


async def new_review(*, organizer_id: int, event_id: int, event_title: str, stars_count: int) -> None:
    await deliver([NotificationCreate(
        user_id=organizer_id,
        type=NotificationType.NEW_REVIEW,
        message=f"New {stars_count}-star review on '{event_title}'.",
        event_id=event_id,
    )])


async def review_mentions(*, author_id: int, user_ids: list[int], event_id: int, event_title: str) -> None:
    try:
        async with AsyncSessionLocal() as db:
            valid_ids = await UserRepository(db).get_active_ids(list(set(user_ids)))
    except Exception:
        logger.exception("Could not validate mentioned users")
        return
    await deliver([
        NotificationCreate(
            user_id=uid,
            type=NotificationType.REVIEW_MENTION,
            message=f"You were mentioned in a review of '{event_title}'.",
            event_id=event_id,
        )
        for uid in valid_ids
        if uid != author_id
    ])