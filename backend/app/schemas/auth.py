from pydantic import BaseModel, EmailStr, Field, field_validator, SecretStr

def check_password_mix_helper(v: SecretStr) -> SecretStr:
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

def normalise_email_helper(v: str) -> str:
    return v.strip().lower()

class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=128)


    @field_validator("email")
    @classmethod
    def normalise_email(cls, v: str) -> str:
        return normalise_email_helper(v)

    @field_validator("password")
    @classmethod
    def check_password_mix(cls, v: SecretStr) -> SecretStr:
        return check_password_mix_helper(v)