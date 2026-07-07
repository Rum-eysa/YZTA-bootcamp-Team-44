"""Reference repository"""

from typing import List

from app.models import Reference
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ReferenceRepository(BaseRepository[Reference]):
    def __init__(self, session: AsyncSession):
        super().__init__(Reference, session)

    async def list_by_user(self, user_id: str) -> List[Reference]:
        result = await self.session.execute(
            select(Reference)
            .where(Reference.user_id == user_id)
            .order_by(Reference.created_at.desc())
        )
        return list(result.scalars().all())

