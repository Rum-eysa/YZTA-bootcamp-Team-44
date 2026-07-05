"""CV Üretim Ajanı'nı tetikleyen endpoint"""
import json

from app.agents.cv_generation import CVGenerationAgent, get_cv_generation_agent
from app.database import get_db
from app.dependencies import get_current_user_id
from app.models import JobListing
from app.schemas.cv_generation import CVGenerationRequest, CVGenerationResponse
from app.services.user import get_user_by_id
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["CV Generation"])


@router.post("/generate-cv", response_model=CVGenerationResponse)
async def generate_cv(
    payload: CVGenerationRequest,
    user_id: str = Depends(get_current_user_id),
    agent: CVGenerationAgent = Depends(get_cv_generation_agent),
    db: AsyncSession = Depends(get_db),
):
    """Kullanıcı profili + ilan analizine göre LaTeX/Tectonic ile PDF CV üretir, MinIO'ya yükler"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    listing = await db.get(JobListing, payload.listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    user_profile = {
        "full_name": user.full_name,
        "email": user.email,
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
    )

    return CVGenerationResponse(
        document_id=document.id,
        listing_id=listing.id,
        cv_url=document.cv_url,
    )
