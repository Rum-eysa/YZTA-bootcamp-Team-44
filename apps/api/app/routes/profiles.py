"""User profile routes (US-008 alias)"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user_id
from app.routes.users import update_current_user
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(tags=["Profiles"])


@router.patch("/me", response_model=UserResponse)
async def patch_profile(
    user_update: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile (US-008 alias for PATCH /api/profiles/me)."""
    return await update_current_user(user_update, user_id, db)
