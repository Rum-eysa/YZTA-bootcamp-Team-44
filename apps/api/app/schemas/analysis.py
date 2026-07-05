"""Analiz Ajanı endpoint şemaları"""
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, model_validator


class AnalyzeRequest(BaseModel):
    listing_text: Optional[str] = Field(None, max_length=20_000, description="İlan metni")
    listing_url: Optional[HttpUrl] = Field(None, description="İlan URL'si")
    company_name: Optional[str] = Field(None, max_length=255, description="Başvurulan şirket adı")

    @model_validator(mode="after")
    def validate_text_or_url(self):
        text = (self.listing_text or "").strip()
        url = self.listing_url
        if not text and not url:
            raise ValueError("listing_text veya listing_url alanlarından en az biri zorunludur")
        if text and len(text) < 50:
            raise ValueError("listing_text en az 50 karakter olmalıdır")
        return self


class AnalyzeResponse(BaseModel):
    listing_id: str
    required_skills: list[str]
    nice_to_have: list[str]
    seniority: str
    position_title: str
    confidence: float
