"""WorkExperience repository (US-013)"""

from typing import List

from app.models import WorkExperience
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class WorkExperienceRepository(BaseRepository[WorkExperience]):
    """Repository for WorkExperience model"""

    def __init__(self, session: AsyncSession):
        super().__init__(WorkExperience, session)

    async def list_by_user(self, user_id: str) -> List[WorkExperience]:
        """Bir kullanıcıya ait tüm iş deneyimleri (yeniden eskiye)"""
        result = await self.session.execute(
            select(WorkExperience)
            .where(WorkExperience.user_id == user_id)
            .order_by(WorkExperience.start_date.desc().nullslast())
        )
        return list(result.scalars().all())
