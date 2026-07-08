"""Eşleştirme Ajanı'nı tetikleyen endpoint"""
import json

from app.agents.matching import MatchingAgent, get_matching_agent
from app.database import get_db
from app.dependencies import get_current_user_id
from app.repositories.match import MatchRepository
from app.schemas.match import MatchRequest, MatchResponse
from app.services.context import (
    ContextManager,
    job_analysis_from_context,
    user_profile_for_matching,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Matching"])


@router.post("/match", response_model=MatchResponse)
async def match_listing(
    payload: MatchRequest,
    user_id: str = Depends(get_current_user_id),
    agent: MatchingAgent = Depends(get_matching_agent),
    db: AsyncSession = Depends(get_db),
):
    """Kullanıcı profili ile ilanı eşleştirir, matches tablosuna kaydeder (cache'li)"""
    match_repo = MatchRepository(db)
    cached = await match_repo.get_by_user_and_listing(user_id, payload.listing_id)
    if cached:
        return MatchResponse(
            match_id=cached.id,
            listing_id=payload.listing_id,
            score=cached.score,
            matched_skills=json.loads(cached.matched_skills) if cached.matched_skills else [],
            missing_skills=json.loads(cached.missing_skills) if cached.missing_skills else [],
            score_breakdown=json.loads(cached.score_breakdown) if cached.score_breakdown else None,
            cached=True,
        )

    context_manager = ContextManager(db)
    try:
        context = await context_manager.load(user_id, payload.listing_id)
    except ValueError as exc:
        detail = str(exc)
        if "User not found" in detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        ) from exc

    user_profile = user_profile_for_matching(context)
    job_analysis = job_analysis_from_context(context)

    match = await agent.match_and_save(
        db=db,
        user_id=user_id,
        listing_id=payload.listing_id,
        user_profile=user_profile,
        job_analysis=job_analysis,
    )

    return MatchResponse(
        match_id=match.id,
        listing_id=payload.listing_id,
        score=match.score,
        matched_skills=json.loads(match.matched_skills) if match.matched_skills else [],
        missing_skills=json.loads(match.missing_skills) if match.missing_skills else [],
        score_breakdown=json.loads(match.score_breakdown) if match.score_breakdown else None,
        cached=False,
    )
