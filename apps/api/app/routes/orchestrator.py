"""Orkestratör endpoint'i: tek istekte analiz -> eşleşme -> önyazı -> CV (US-030)"""

from app.agents.orchestrator import ApplicationOrchestrator, OrchestrationError, get_orchestrator
from app.database import get_db
from app.dependencies import get_current_user_id
from app.observability import audit_event
from app.rate_limit import enforce_rate_limit
from app.schemas.orchestrator import ProcessRequest, ProcessResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Orchestrator"])


@router.post("/process", response_model=ProcessResponse)
async def process_application(
    payload: ProcessRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    orchestrator: ApplicationOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_db),
):
    """Tam başvuru akışını tek çağrıda koordine eder; kısmi sonuçlara dayanıklıdır"""
    await enforce_rate_limit(request, suffix="process", limit=5, window_seconds=60)
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

    # cv_url orchestrator içinde document_id ile API path'e çevrilir
    audit_event(
        "process_application",
        user_id=user_id,
        listing_id=result.get("listing_id"),
    )
    return ProcessResponse(**result)
