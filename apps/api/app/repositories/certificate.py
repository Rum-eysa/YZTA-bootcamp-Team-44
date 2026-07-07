"""Certificate repository"""

from typing import List

from app.models import Certificate
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CertificateRepository(BaseRepository[Certificate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Certificate, session)

    async def list_by_user(self, user_id: str) -> List[Certificate]:
        result = await self.session.execute(
            select(Certificate)
            .where(Certificate.user_id == user_id)
            .order_by(Certificate.issue_date.desc().nullslast())
        )
        return list(result.scalars().all())

