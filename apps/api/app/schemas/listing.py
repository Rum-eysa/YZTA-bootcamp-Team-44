"""İlan (job listing) listeleme / detay / güncelleme şemaları (US-052† + US-053†)"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

APPLICATION_STAGES = {"review", "interview", "technical_test", "offer", "rejected"}


class ListingSummary(BaseModel):
    """İlanlarım listesi için özet kayıt."""

    id: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    seniority: Optional[str] = None
    application_stage: str = "review"
    analysis_status: Optional[str] = None
    score: Optional[float] = Field(None, description="Eşleşme skoru (0-100), hesaplandıysa")
    created_at: datetime


class ListingDocument(BaseModel):
    id: str
    doc_type: str
    cv_url: Optional[str] = None
    cover_letter_text: Optional[str] = None


class ListingDetail(BaseModel):
    """Tek ilan detay yanıtı (düzenleme sayfası için)."""

    id: str
    title: Optional[str] = None
    company: Optional[str] = None
    raw_text: Optional[str] = None
    seniority: Optional[str] = None
    analysis_status: Optional[str] = None

    required_skills: List[str] = []
    nice_to_have: List[str] = []

    location: Optional[str] = None
    employment_type: Optional[str] = None
    company_about: Optional[str] = None
    extra_notes: Optional[str] = None
    benefits: List[str] = []
    experience_level: Optional[str] = None
    education_level: Optional[str] = None
    military_status: Optional[str] = None
    languages: List[str] = []
    driver_license: Optional[str] = None
    application_stage: str = "review"

    score: Optional[float] = None
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    documents: List[ListingDocument] = []

    created_at: datetime
    updated_at: datetime


class ListingUpdate(BaseModel):
    """İlan güncelleme (kısmi) - yalnızca sahibi."""

    title: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    raw_text: Optional[str] = Field(None, max_length=20_000)
    location: Optional[str] = Field(None, max_length=255)
    employment_type: Optional[str] = Field(None, max_length=100)
    company_about: Optional[str] = None
    extra_notes: Optional[str] = None
    benefits: Optional[List[str]] = None
    experience_level: Optional[str] = Field(None, max_length=50)
    education_level: Optional[str] = Field(None, max_length=50)
    military_status: Optional[str] = Field(None, max_length=50)
    languages: Optional[List[str]] = None
    driver_license: Optional[str] = Field(None, max_length=50)
    application_stage: Optional[str] = Field(None, max_length=30)
