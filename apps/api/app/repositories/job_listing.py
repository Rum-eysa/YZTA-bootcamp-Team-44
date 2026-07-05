"""Job listing repository"""
from app.models import JobListing
from app.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class JobListingRepository(BaseRepository[JobListing]):
    """Repository for JobListing model"""

    def __init__(self, session: AsyncSession):
        super().__init__(JobListing, session)
