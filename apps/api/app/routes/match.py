"""Eşleştirme Ajanı'nı tetikleyen endpoint"""
import json

from app.agents.matching import MatchingAgent, get_matching_agent
from app.database import get_db
from app.dependencies import get_current_user_id
from app.models import JobListing, WorkExperience, Project
from app.repositories.match import MatchRepository
from app.schemas.match import MatchRequest, MatchResponse
from app.services.user import get_user_by_id
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
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
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    listing = await db.get(JobListing, payload.listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

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

    # Work experiences ve projects verilerini çek
    work_experiences_result = await db.execute(
        select(WorkExperience).where(WorkExperience.user_id == user_id)
    )
    work_experiences = [
        {
            "company": exp.company,
            "title": exp.title,
            "description": exp.description,
        }
        for exp in work_experiences_result.scalars().all()
    ]

    projects_result = await db.execute(
        select(Project).where(Project.user_id == user_id)
    )
    projects = [
        {
            "title": proj.title,
            "description": proj.description,
            "tech_stack": json.loads(proj.tech_stack) if proj.tech_stack else [],
        }
        for proj in projects_result.scalars().all()
    ]

    user_profile = {
        "skills": json.loads(user.skills) if user.skills else [],
        "seniority": user.seniority,
        "work_experiences": work_experiences,
        "projects": projects,
    }
    job_analysis = json.loads(listing.parsed_json) if listing.parsed_json else {}

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
