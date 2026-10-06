from pydantic import BaseModel, EmailStr, Field, ConfigDict, SecretStr, field_validator
from app.core.enums import UserRole
from typing import Annotated

class UserResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: int
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    role: UserRole
    is_active: bool

class UserUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    id: int | None = None
    name: Annotated[str | None, Field(min_length=1, max_length=50)] = None
    email: EmailStr | None = None
    password: SecretStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None

class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=20)

    @field_validator("password")
    @classmethod
    def check_password_mix(cls, v: SecretStr) -> SecretStr:
        pwd = v.get_secret_value()

        errors = []
        if not any(c.isupper() for c in pwd):
            errors.append("at least one uppercase letter")
        if not any(c.islower() for c in pwd):
            errors.append("at least one lowercase letter")
        if not any(c.isdigit() for c in pwd):
            errors.append("at least one digit")

        if errors:
            raise ValueError(f"Password must contain: {', '.join(errors)}.")

        return v