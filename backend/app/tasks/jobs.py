import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.core.enums import NotificationType
from app.db.session import AsyncSessionLocal
from app.repositories.event import EventRepository
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationCreate
from app.tasks.notifications import push, to_payloads

logger = logging.getLogger(__name__)

REMINDER_LEAD_TIME = timedelta(hours=24)
JOB_INTERVAL_SECONDS = 300


async def send_event_reminders() -> None:
    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        events = await EventRepository(db).claim_due_for_reminder(
            now=now, lead_time=REMINDER_LEAD_TIME
        )

        items: list[NotificationCreate] = []
        for event in events:
            starts_at = event.time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            for booking in event.bookings:
                if booking.is_active:
                    items.append(NotificationCreate(
                        user_id=booking.user_id,
                        type=NotificationType.EVENT_REMINDER,
                        message=f"Reminder: '{event.title}' starts at {starts_at}.",
                        event_id=event.id,
                    ))
            event.reminder_sent = True

        db_notifications = await NotificationRepository(db).create_many(items) if items else []
        payloads = to_payloads(db_notifications)
        await db.commit()

    await push(payloads)


async def complete_past_events() -> None:
    now = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as db:
        completed = await EventRepository(db).mark_past_as_completed(now=now)
        await db.commit()
    if completed:
        logger.info("Marked %d event(s) as completed", completed)


async def _run_every(seconds: float, job) -> None:
    while True:
        try:
            await job()
        except Exception:
            logger.exception("Scheduled job %s failed", job.__name__)
        await asyncio.sleep(seconds)


def start_scheduled_jobs() -> list[asyncio.Task]:
    return [
        asyncio.create_task(_run_every(JOB_INTERVAL_SECONDS, send_event_reminders), name="send_event_reminders"),
        asyncio.create_task(_run_every(JOB_INTERVAL_SECONDS, complete_past_events), name="complete_past_events"),
    ]


async def stop_scheduled_jobs(tasks: list[asyncio.Task]) -> None:
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)