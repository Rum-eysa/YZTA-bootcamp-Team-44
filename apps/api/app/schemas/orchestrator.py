"""Orkestratör endpoint şemaları (US-030, response şekli US-041 ile güncellendi)"""

from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


class ProcessRequest(BaseModel):
    listing_text: Optional[str] = Field(None, max_length=20_000, description="Yeni ilan metni")
    listing_id: Optional[str] = Field(None, description="Daha önce analiz edilmiş ilan id'si")
    company_name: Optional[str] = Field(None, max_length=255)
    generate_cover_letter: bool = True
    generate_cv: bool = True

    @model_validator(mode="after")
    def validate_text_or_id(self):
        text = (self.listing_text or "").strip()
        if not text and not self.listing_id:
            raise ValueError("listing_text veya listing_id alanlarından biri zorunludur")
        if text and len(text) < 50:
            raise ValueError("listing_text en az 50 karakter olmalıdır")
        return self


class TimelineStep(BaseModel):
    step: str
    status: str
    duration_ms: float
    attempts: Optional[int] = None
    error: Optional[str] = None


class ProcessResponse(BaseModel):
    """US-041 kabul kriteri: listing_id, match, cv_url, cover_letter_text, errors[]"""

    listing_id: str
    match: dict[str, Any]
    cv_url: Optional[str] = None
    cover_letter_text: Optional[str] = None
    errors: list[str] = []

    # Ek gözlemlenebilirlik alanları (AC'yi kırmaz, hata ayıklama için)
    analysis: dict[str, Any]
    timeline: list[TimelineStep]
