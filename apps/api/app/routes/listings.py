"""İlan (job listing) listeleme, detay ve düzenleme endpoint'leri (US-052† + US-053†)

Not: analiz sonucunu DB'den okuma + created_by/JWT US-014 ile örtüşür.
"""
import json
from typing import Any, List, Optional

from app.database import get_db
from app.dependencies import get_current_user_id
from app.models import Document, JobListing
from app.repositories.job_listing import JobListingRepository
from app.repositories.match import MatchRepository
from app.schemas.listing import (
    APPLICATION_STAGES,
    ListingDetail,
    ListingDocument,
    ListingSummary,
    ListingUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Listings"])


def _load_list(value: Optional[str]) -> List[str]:
    """JSON string kolonu güvenli şekilde list[str]'e çevirir."""
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError):
        return []
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    return []


async def _get_owned_listing(
    listing_id: str, user_id: str, repo: JobListingRepository
) -> JobListing:
    listing = await repo.get(listing_id)
    if not listing or listing.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İlan bulunamadı")
    return listing


@router.get("", response_model=List[ListingSummary])
async def list_my_listings(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Mevcut kullanıcının oluşturduğu tüm ilanları listeler (İlanlarım)."""
    repo = JobListingRepository(db)
    match_repo = MatchRepository(db)
    listings = await repo.list_by_user(user_id)

    summaries: List[ListingSummary] = []
    for listing in listings:
        match = await match_repo.get_by_user_and_listing(user_id, listing.id)
        summaries.append(
            ListingSummary(
                id=listing.id,
                title=listing.title,
                company=listing.company,
                location=listing.location,
                seniority=listing.seniority,
                application_stage=listing.application_stage or "review",
                analysis_status=listing.analysis_status,
                score=match.score if match else None,
                created_at=listing.created_at,
            )
        )
    return summaries


@router.get("/{listing_id}", response_model=ListingDetail)
async def get_listing(
    listing_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Tek bir ilanın detayını DB'den döner (yalnızca sahibi)."""
    repo = JobListingRepository(db)
    listing = await _get_owned_listing(listing_id, user_id, repo)

    match_repo = MatchRepository(db)
    match = await match_repo.get_by_user_and_listing(user_id, listing.id)

    docs_result = await db.execute(
        select(Document).where(Document.listing_id == listing.id, Document.user_id == user_id)
    )
    documents = [
        ListingDocument(
            id=doc.id,
            doc_type=doc.doc_type,
            cv_url=doc.cv_url,
            cover_letter_text=doc.cover_letter_text,
        )
        for doc in docs_result.scalars().all()
    ]

    return ListingDetail(
        id=listing.id,
        title=listing.title,
        company=listing.company,
        raw_text=listing.raw_text,
        seniority=listing.seniority,
        analysis_status=listing.analysis_status,
        required_skills=_load_list(listing.required_skills),
        nice_to_have=_load_list(listing.nice_to_have_skills),
        location=listing.location,
        employment_type=listing.employment_type,
        company_about=listing.company_about,
        extra_notes=listing.extra_notes,
        benefits=_load_list(listing.benefits),
        experience_level=listing.experience_level,
        education_level=listing.education_level,
        military_status=listing.military_status,
        languages=_load_list(listing.languages),
        driver_license=listing.driver_license,
        application_stage=listing.application_stage or "review",
        score=match.score if match else None,
        matched_skills=_load_list(match.matched_skills) if match else [],
        missing_skills=_load_list(match.missing_skills) if match else [],
        documents=documents,
        created_at=listing.created_at,
        updated_at=listing.updated_at,
    )


@router.patch("/{listing_id}", response_model=ListingDetail)
async def update_listing(
    listing_id: str,
    payload: ListingUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """İlanın düzenlenebilir alanlarını günceller (yalnızca sahibi)."""
    repo = JobListingRepository(db)
    listing = await _get_owned_listing(listing_id, user_id, repo)

    update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

    stage = update_data.get("application_stage")
    if stage is not None and stage not in APPLICATION_STAGES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Geçersiz başvuru aşaması: {stage}",
        )

    for field in ("benefits", "languages"):
        if field in update_data and update_data[field] is not None:
            update_data[field] = json.dumps(update_data[field], ensure_ascii=False)

    for field, value in update_data.items():
        setattr(listing, field, value)
    await repo.update(listing.id, listing)

    return await get_listing(listing_id, user_id, db)
