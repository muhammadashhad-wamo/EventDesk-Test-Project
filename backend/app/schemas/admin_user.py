from pydantic import BaseModel, ConfigDict

from app.core.enums import UserRole


class RoleUpdate(BaseModel):
    role: UserRole