"""Önyazı Ajanı'nı tetikleyen endpoint"""
from app.agents.cover_letter import CoverLetterAgent, get_cover_letter_agent
from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.cover_letter import CoverLetterRequest, CoverLetterResponse
from app.services.context import (
    ContextManager,
    job_analysis_from_context,
    matching_gaps_from_context,
    user_profile_for_agents,
)
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
    """Kullanıcı profili + ilan analizi ile şirkete özel önyazı üretir, documents'a kaydeder"""
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

    user_profile = user_profile_for_agents(context)
    job_analysis = job_analysis_from_context(context)
    matching_gaps = matching_gaps_from_context(context)

    document = await agent.generate_and_save(
        db=db,
        user_id=user_id,
        listing_id=context["listing"]["id"],
        user_profile=user_profile,
        job_analysis=job_analysis,
        matching_gaps=matching_gaps,
        tone_preference=context["user"].get("tone_preference") or "professional",
        company_name=context["listing"].get("company"),
        extra_prompt=payload.extra_prompt,
    )

    return CoverLetterResponse(
        document_id=document.id,
        listing_id=context["listing"]["id"],
        company_name=context["listing"].get("company") or "belirtilen şirket",
        cover_letter_text=document.cover_letter_text,
    )
