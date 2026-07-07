"""Language repository"""

from typing import List

from app.models import Language
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class LanguageRepository(BaseRepository[Language]):
    def __init__(self, session: AsyncSession):
        super().__init__(Language, session)

    async def list_by_user(self, user_id: str) -> List[Language]:
        result = await self.session.execute(
            select(Language).where(Language.user_id == user_id).order_by(Language.created_at.desc())
        )
        return list(result.scalars().all())

