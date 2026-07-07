"""Job listing repository"""
from typing import List

from app.models import JobListing
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class JobListingRepository(BaseRepository[JobListing]):
    """Repository for JobListing model"""

    def __init__(self, session: AsyncSession):
        super().__init__(JobListing, session)

    async def list_by_user(self, user_id: str) -> List[JobListing]:
        """Bir kullanıcının oluşturduğu tüm ilanları (yeni → eski) döner."""
        result = await self.session.execute(
            select(JobListing)
            .where(JobListing.created_by == user_id)
            .order_by(JobListing.created_at.desc())
        )
        return list(result.scalars().all())
