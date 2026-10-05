from pydantic import BaseModel, EmailStr, Field, field_validator, SecretStr

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

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"