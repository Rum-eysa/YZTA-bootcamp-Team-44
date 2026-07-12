"""Orkestratör endpoint'i: tek istekte analiz -> eşleşme -> önyazı -> CV (US-030)"""

from app.agents.orchestrator import ApplicationOrchestrator, OrchestrationError, get_orchestrator
from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.orchestrator import ProcessRequest, ProcessResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Orchestrator"])


@router.post("/process", response_model=ProcessResponse)
async def process_application(
    payload: ProcessRequest,
    user_id: str = Depends(get_current_user_id),
    orchestrator: ApplicationOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_db),
):
    """Tam başvuru akışını tek çağrıda koordine eder; kısmi sonuçlara dayanıklıdır"""
    try:
        result = await orchestrator.process(
            db=db,
            user_id=user_id,
            listing_text=payload.listing_text,
            listing_id=payload.listing_id,
            company_name=payload.company_name,
            generate_cover_letter=payload.generate_cover_letter,
            generate_cv=payload.generate_cv,
        )
    except OrchestrationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Akışın '{exc.step}' adımı başarısız: {exc.detail}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ProcessResponse(**result)
