"""Misafir ATS CV uyumluluk kontrolü endpoint'i (auth yok, günlük 1/IP)."""
from app.agents.ats_check import AtsCheckAgent, extract_pdf_text, get_ats_check_agent
from app.exceptions import ValidationException
from app.rate_limit import enforce_rate_limit
from app.schemas.ats_check import AtsCheckResponse
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

router = APIRouter(tags=["ATS Check"])

_MAX_BYTES = 5 * 1024 * 1024
_ALLOWED_TYPES = {"application/pdf", "application/x-pdf"}


def _is_pdf(data: bytes, content_type: str, filename: str) -> bool:
    if data.startswith(b"%PDF"):
        return True
    name = (filename or "").lower()
    if name.endswith(".pdf") and (not content_type or content_type in _ALLOWED_TYPES):
        return True
    return content_type in _ALLOWED_TYPES and data[:4] == b"%PDF"


@router.post("/ats-check", response_model=AtsCheckResponse)
async def check_ats_compatibility(
    request: Request,
    file: UploadFile = File(...),
    agent: AtsCheckAgent = Depends(get_ats_check_agent),
):
    """Kayıt olmadan PDF CV ATS uyumluluğunu puanlar. IP başına günde 1 istek."""
    content_type = (file.content_type or "").lower()
    data = await file.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Boş dosya yüklenemez",
        )
    if len(data) > _MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CV en fazla 5MB olabilir",
        )
    if not _is_pdf(data, content_type, file.filename or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece PDF dosyası yüklenebilir",
        )

    # Geçersiz/metinsiz PDF günlük hakkı tüketmesin
    try:
        extract_pdf_text(data)
    except ValidationException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.detail,
        ) from exc

    await enforce_rate_limit(
        request,
        suffix="ats_check",
        limit=1,
        window_seconds=86400,
    )

    result = await agent.analyze(data)
    return AtsCheckResponse(**result)
