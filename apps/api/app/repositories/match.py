"""Match repository"""
from app.models import Match
from app.repositories.base import BaseRepository
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


class MatchRepository(BaseRepository[Match]):
    """Repository for Match model"""

    def __init__(self, session: AsyncSession):
        super().__init__(Match, session)

    async def get_by_user_and_listing(self, user_id: str, listing_id: str):
        """Aynı ilan için cache edilmiş eşleştirme sonucu var mı"""
        result = await self.session.execute(
            select(Match).where(Match.user_id == user_id, Match.listing_id == listing_id)
        )
        return result.scalar_one_or_none()

    async def delete_by_user_and_listing(self, user_id: str, listing_id: str) -> int:
        """İlan yeniden analiz edildiğinde/eşleşme zorla güncellendiğinde eski cache'i siler
        (US-037: required_skills değiştiğinde eski match artık geçersizdir)"""
        result = await self.session.execute(
            delete(Match).where(Match.user_id == user_id, Match.listing_id == listing_id)
        )
        await self.session.commit()
        return result.rowcount
