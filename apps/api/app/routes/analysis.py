"""Analiz Ajanı'nı tetikleyen endpoint"""
import json

from app.agents.listing_analysis import AnalyzeListingAgent, get_listing_analysis_agent
from app.database import get_db
from app.models import JobListing
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_listing(
    payload: AnalyzeRequest,
    agent: AnalyzeListingAgent = Depends(get_listing_analysis_agent),
    db: AsyncSession = Depends(get_db),
):
    """İlan metnini Analiz Ajanı ile ayrıştırır, job_listings tablosuna kaydeder"""
    result = await agent.analyze(payload.listing_text)

    listing = JobListing(
        title=result.get("position_title"),
        company=payload.company_name,
        raw_text=payload.listing_text,
        required_skills=json.dumps(result.get("required_skills") or [], ensure_ascii=False),
        nice_to_have_skills=json.dumps(result.get("nice_to_have_skills") or [], ensure_ascii=False),
        seniority=result.get("seniority"),
        parsed_json=json.dumps(result, ensure_ascii=False),
        analysis_status="completed",
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
