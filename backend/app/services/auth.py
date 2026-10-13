from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.repositories.user import UserRepository
from app.schemas.auth import RegisterRequest
from app.schemas.token import TokenPair
from app.schemas.user import UserResponse

from app.core.enums import UserRole

from app.services.token import TokenService

from sqlalchemy.exc import IntegrityError


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
        except IntegrityError:
            await self.db.rollback()
            # Returning 409 in case of IntegrityError being raised due to duplicate emails
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Email already registered"
            )

        user_schema = UserResponse.model_validate(db_user)
        return user_schema

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self.users.get_by_email(email.lower())

        if not user:
            # Comparing password with a dummy hash so this request takes the same time as a request having a valid user email
            dummy_hash = '$argon2id$v=19$m=65536,t=3,p=4$RV6/TvbzVF0ycuhUy3shDA$dPY54HbTwgWxeHV9ksb2skobyIibvPQ2iQ7uCTboums'
            verify_password(password, dummy_hash)
            raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    "Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is deactivated")

        return await TokenService(self.db).issue(user_id=user.id)