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

class AuditAction(StrEnum):
    EVENT_CREATED = "event.created"
    EVENT_UPDATED = "event.updated"
    EVENT_CANCELLED = "event.cancelled"
    EVENT_DELETED = "event.deleted"
    BOOKING_CREATED = "booking.created"
    BOOKING_CANCELLED = "booking.cancelled"
    USER_ROLE_CHANGED = "user.role_changed"


class AuditEntity(StrEnum):
    EVENT = "event"
    USER = "user"