"""SocialLink repository"""

from typing import List

from app.models import SocialLink
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SocialLinkRepository(BaseRepository[SocialLink]):
    def __init__(self, session: AsyncSession):
        super().__init__(SocialLink, session)

    async def list_by_user(self, user_id: str) -> List[SocialLink]:
        result = await self.session.execute(
            select(SocialLink)
            .where(SocialLink.user_id == user_id)
            .order_by(SocialLink.created_at.desc())
        )
        return list(result.scalars().all())

