from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"

class EventStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"