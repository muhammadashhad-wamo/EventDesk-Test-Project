from pydantic import BaseModel, ConfigDict

from app.core.enums import UserRole


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool


class RoleUpdate(BaseModel):
    role: UserRole