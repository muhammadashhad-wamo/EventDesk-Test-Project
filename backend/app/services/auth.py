from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.repositories.user import UserRepository
from app.schemas.auth import RegisterRequest
from app.schemas.token import TokenPair
from app.schemas.user import UserResponse

from app.core.enums import UserRole

from app.services.token import TokenService


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    async def register(self, data: RegisterRequest) -> UserResponse:
        if await self.users.get_by_email(data.email.lower()):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

        try:
            db_user = await self.users.create(
                name=data.name,
                email=data.email.lower(),
                password_hash=hash_password(data.password.get_secret_value()),
                role=UserRole.USER,
            )
            await self.db.commit()
        except:
            await self.db.rollback()
            raise

        user_schema = UserResponse.model_validate(db_user)
        return user_schema

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self.users.get_by_email(email.lower())

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is deactivated")

        return await TokenService(self.db).issue(user_id=user.id)