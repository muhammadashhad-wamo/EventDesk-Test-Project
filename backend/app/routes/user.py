from fastapi import APIRouter

from app.core.dependencies import CurrentUser
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user