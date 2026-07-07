"""Analiz Ajanı'nı tetikleyen endpoint"""
import json

from app.agents.listing_analysis import AnalyzeListingAgent, get_listing_analysis_agent
from app.database import get_db
from app.dependencies import get_current_user_id
from app.models import JobListing
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.listing_fetch import fetch_listing_text_from_url
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_listing(
    payload: AnalyzeRequest,
    agent: AnalyzeListingAgent = Depends(get_listing_analysis_agent),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """İlan metnini veya URL'sini Analiz Ajanı ile ayrıştırır, job_listings tablosuna kaydeder"""
    listing_text = (payload.listing_text or "").strip()
    if not listing_text and payload.listing_url:
        listing_text = await fetch_listing_text_from_url(str(payload.listing_url))

    result = await agent.analyze(listing_text)

    listing = JobListing(
        created_by=user_id,
        title=(payload.position_title or "").strip() or result.get("position_title"),
        company=payload.company_name,
        raw_text=listing_text,
        required_skills=json.dumps(result.get("required_skills") or [], ensure_ascii=False),
        nice_to_have_skills=json.dumps(result.get("nice_to_have_skills") or [], ensure_ascii=False),
        seniority=result.get("seniority"),
        parsed_json=json.dumps(result, ensure_ascii=False),
        analysis_status="completed",
        location=payload.location,
        employment_type=payload.employment_type,
        company_about=payload.company_about,
        extra_notes=payload.extra_notes,
        benefits=json.dumps(payload.benefits, ensure_ascii=False) if payload.benefits else None,
        experience_level=payload.experience_level,
        education_level=payload.education_level,
        military_status=payload.military_status,
        languages=json.dumps(payload.languages, ensure_ascii=False) if payload.languages else None,
        driver_license=payload.driver_license,
    )
    db.add(listing)
    await db.commit()
    await db.refresh(listing)

    return AnalyzeResponse(
        listing_id=listing.id,
        required_skills=result.get("required_skills") or [],
        nice_to_have=result.get("nice_to_have_skills") or [],
        seniority=result.get("seniority") or "",
        position_title=result.get("position_title") or "",
        confidence=result.get("confidence") or 0.0,
    )
