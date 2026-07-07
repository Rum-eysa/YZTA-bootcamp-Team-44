"""Education repository"""

from typing import List

from app.models import EducationRecord
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class EducationRepository(BaseRepository[EducationRecord]):
    def __init__(self, session: AsyncSession):
        super().__init__(EducationRecord, session)

    async def list_by_user(self, user_id: str) -> List[EducationRecord]:
        result = await self.session.execute(
            select(EducationRecord)
            .where(EducationRecord.user_id == user_id)
            .order_by(EducationRecord.start_date.desc().nullslast())
        )
        return list(result.scalars().all())
