from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        user_id: int,
        token_hash: str,
        created_at: datetime,
        expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            created_at=created_at,
            expires_at=expires_at,
        )
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        statement = (
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
        )
        return await self.db.scalar(statement)

    async def revoke_all_for_user(self, *, user_id: int, now: datetime) -> None:
        statement = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self.db.execute(statement)

    async def revoke_if_active(self, *, token_id: int, now: datetime) -> bool:
        result = await self._db.execute(
            update(RefreshToken)
            .where(RefreshToken.id == token_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
            .execution_options(synchronize_session=False)
        )
        return result.rowcount == 1

    async def delete_expired(self, *, now: datetime) -> int:
        result = await self._db.execute(
            delete(RefreshToken)
            .where(RefreshToken.expires_at <= now)
            .execution_options(synchronize_session=False)
        )
        return result.rowcount