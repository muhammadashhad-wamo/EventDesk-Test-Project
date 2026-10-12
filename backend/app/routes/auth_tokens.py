from fastapi import APIRouter, status

from app.core.dependencies import DbSession
from app.schemas.token import RefreshRequest, TokenPair
from app.services.token import TokenService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(data: RefreshRequest, db: DbSession):
    return await TokenService(db).refresh(raw_token=data.refresh_token)