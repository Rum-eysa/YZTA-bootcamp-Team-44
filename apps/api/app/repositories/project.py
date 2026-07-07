"""Project repository (US-013)"""

from typing import List

from app.models import Project
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model"""

    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

    async def list_by_user(self, user_id: str) -> List[Project]:
        """Bir kullanıcıya ait tüm projeler (yeniden eskiye)"""
        result = await self.session.execute(
            select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())
