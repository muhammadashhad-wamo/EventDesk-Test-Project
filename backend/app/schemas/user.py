from pydantic import BaseModel, EmailStr, Field, ConfigDict, SecretStr, field_validator
from app.core.enums import UserRole
from typing import Annotated
from app.schemas.auth import check_password_mix_helper, normalise_email_helper

class UserResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)

    id: int
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    role: UserRole
    is_active: bool

class UserBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)

    id: int
    name: Annotated[str, Field(min_length=1, max_length=50)]
    email: EmailStr
    password_hash: str
    role: UserRole
    is_active: bool

class UserUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=50)] = None
    email: Annotated[EmailStr, Field(max_length=255)] | None = None

    @field_validator("email")
    @classmethod
    def normalise_email(cls, v: str | None) -> str | None:
        return normalise_email_helper(v)

class ChangePasswordRequest(BaseModel):
    current_password: SecretStr = Field(min_length=8, max_length=128)
    new_password: SecretStr = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def check_password_mix(cls, v: SecretStr) -> SecretStr:
        return check_password_mix_helper(v)

class UserLookupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str