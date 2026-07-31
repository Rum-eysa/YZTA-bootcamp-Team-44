"""Korumalı belge indirme — JWT + sahiplik zorunlu; MinIO URL'leri tarayıcıya sızmaz."""

from app.database import get_db
from app.dependencies import get_current_user_id
from app.models import Document
from app.observability import audit_event
from app.services.storage import get_storage_service
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/{document_id}/file")
async def download_document_file(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """CV PDF'ini yalnızca sahibi JWT ile indirebilir / önizleyebilir."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document or document.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Belge bulunamadı")
    if document.doc_type != "cv" or not document.cv_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Belge bulunamadı")

    storage = get_storage_service()
    pdf_bytes = storage.download_bytes(document.cv_url)
    if not pdf_bytes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dosya depoda bulunamadı",
        )

    audit_event(
        "document_download",
        user_id=user_id,
        document_id=document.id,
        listing_id=document.listing_id,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'inline; filename="CareerTrack-CV.pdf"',
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
