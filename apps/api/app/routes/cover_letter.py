"""Önyazı Ajanı'nı tetikleyen endpoint"""
import json

from app.agents.cover_letter import CoverLetterAgent, get_cover_letter_agent
from app.database import get_db
from app.dependencies import get_current_user_id
from app.models import JobListing
from app.schemas.cover_letter import CoverLetterRequest, CoverLetterResponse
from app.services.user import get_user_by_id
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Cover Letter"])


@router.post("/generate-cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter(
    payload: CoverLetterRequest,
    user_id: str = Depends(get_current_user_id),
    agent: CoverLetterAgent = Depends(get_cover_letter_agent),
    db: AsyncSession = Depends(get_db),
):
    """Kullanıcı profili + ilan analizi ile şirkete özel önyazı üretir, documents tablosuna kaydeder"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    listing = await db.get(JobListing, payload.listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    user_profile = {
        "full_name": user.full_name,
        "target_position": user.target_position,
        "seniority": user.seniority,
        "experience_years": user.experience_years,
        "skills": json.loads(user.skills) if user.skills else [],
        "experience_summary": user.experience_summary,
    }
    job_analysis = json.loads(listing.parsed_json) if listing.parsed_json else {}

    document = await agent.generate_and_save(
        db=db,
        user_id=user_id,
        listing_id=listing.id,
        user_profile=user_profile,
        job_analysis=job_analysis,
        matching_gaps={},
        tone_preference=user.tone_preference or "professional",
        company_name=listing.company,
    )

    return CoverLetterResponse(
        document_id=document.id,
        listing_id=listing.id,
        company_name=listing.company or "belirtilen şirket",
        cover_letter_text=document.cover_letter_text,
    )
