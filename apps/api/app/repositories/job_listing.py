"""Job listing repository"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import JobListing
from app.repositories.base import BaseRepository


class JobListingRepository(BaseRepository[JobListing]):
    """Repository for JobListing model"""

    def __init__(self, session: AsyncSession):
        super().__init__(JobListing, session)
