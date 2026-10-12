import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_refresh_token
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.token import TokenPair

from app.core.config import settings


class TokenService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.tokens = RefreshTokenRepository(db)
        self.users = UserRepository(db)

    async def issue(self, *, user_id: int) -> TokenPair:
        try:
            pair = await self._create_pair(user_id)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise
        return pair

    async def refresh(self, *, raw_token: str) -> TokenPair:
        invalid = HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        now = datetime.now(timezone.utc)

        record = await self.tokens.get_by_hash(hash_refresh_token(raw_token))
        if record is None:
            raise invalid

        if record.revoked_at is not None:
            try:
                await self.tokens.revoke_all_for_user(user_id=record.user_id, now=now)
                await self._db.commit()
            except Exception:
                await self._db.rollback()
                raise
            raise invalid

        if record.expires_at <= now:
            raise invalid

        user = await self.users.get_by_id(record.user_id)
        if user is None or not user.is_active:
            raise invalid

        try:
            record.revoked_at = now
            pair = await self._create_pair(user.id)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise
        return pair

    async def _create_pair(self, user_id: int) -> TokenPair:
        raw_token = secrets.token_urlsafe(48)
        now = datetime.now(timezone.utc)
        await self.tokens.create(
            user_id=user_id,
            token_hash=hash_refresh_token(raw_token),
            created_at=now,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        access_token = create_access_token(user_id)
        return TokenPair(access_token=access_token, refresh_token=raw_token)