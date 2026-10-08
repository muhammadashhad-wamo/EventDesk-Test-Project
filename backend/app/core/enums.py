from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"

class EventStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class NotificationType(StrEnum):
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"
    EVENT_CANCELLED = "event_cancelled"
    EVENT_REMINDER = "event_reminder"
    NEW_REVIEW = "new_review"
    REVIEW_MENTION = "review_mention"