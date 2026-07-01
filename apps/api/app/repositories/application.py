"""Application repository"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Application
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    """Repository for Application model"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Application, session)
    
    async def get_by_user_id(self, user_id: str):
        """Get applications by user ID"""
        result = await self.session.execute(
            select(Application).where(Application.user_id == user_id)
        )
        return list(result.scalars().all())
    
    async def get_by_status(self, status: str):
        """Get applications by status"""
        result = await self.session.execute(
            select(Application).where(Application.status == status)
        )
        return list(result.scalars().all())

