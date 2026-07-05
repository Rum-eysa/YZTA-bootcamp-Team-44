"""Document repository"""
from app.models import Document
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document model"""

    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)

    async def get_by_user(self, user_id: str):
        result = await self.session.execute(select(Document).where(Document.user_id == user_id))
        return list(result.scalars().all())
