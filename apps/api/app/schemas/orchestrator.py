"""Orkestratör endpoint şemaları (US-030)"""

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
    listing_id: str
    analysis: dict[str, Any]
    match: dict[str, Any]
    cover_letter: Optional[dict[str, Any]] = None
    cv: Optional[dict[str, Any]] = None
    timeline: list[TimelineStep]
