"""Exam repository"""

from typing import List

from app.models import Exam
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ExamRepository(BaseRepository[Exam]):
    def __init__(self, session: AsyncSession):
        super().__init__(Exam, session)

    async def list_by_user(self, user_id: str) -> List[Exam]:
        result = await self.session.execute(
            select(Exam).where(Exam.user_id == user_id).order_by(Exam.exam_date.desc().nullslast())
        )
        return list(result.scalars().all())
