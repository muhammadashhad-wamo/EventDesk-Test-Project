from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import RegisterRequest, Token

from app.core.enums import UserRole


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    async def register(self, data: RegisterRequest) -> User:
        if await self.users.get_by_email(data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

        try:
            user = await self.users.create(
                name=data.name,
                email=data.email,
                password_hash=hash_password(data.password.get_secret_value()),
                role=UserRole.USER,
            )
            await self.db.commit()
        except:
            await self.db.rollback()
            raise

        return user

    async def login(self, email: str, password: str) -> Token:
        user = await self.users.get_by_email(email.lower())

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is deactivated")

        return Token(access_token=create_access_token(user.id, user.role))