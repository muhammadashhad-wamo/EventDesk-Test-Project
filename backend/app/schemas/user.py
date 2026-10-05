from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.core.enums import UserRole

class UserResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: int
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    role: UserRole
    is_active: bool