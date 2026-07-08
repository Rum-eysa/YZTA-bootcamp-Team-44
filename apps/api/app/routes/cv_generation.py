"""CV Üretim Ajanı'nı tetikleyen endpoint"""
from app.agents.cv_generation import CVGenerationAgent, get_cv_generation_agent
from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.cv_generation import CVGenerationRequest, CVGenerationResponse
from app.services.context import ContextManager, job_analysis_from_context, user_profile_for_agents
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

    document = await agent.generate_and_save(
        db=db,
        user_id=user_id,
        listing_id=context["listing"]["id"],
        user_profile=user_profile,
        job_analysis=job_analysis,
    )

    return CVGenerationResponse(
        document_id=document.id,
        listing_id=context["listing"]["id"],
        cv_url=document.cv_url,
    )
