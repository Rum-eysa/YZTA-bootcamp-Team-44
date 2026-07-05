"""Önyazı Ajanı endpoint şemaları"""
from pydantic import BaseModel, Field


class CoverLetterRequest(BaseModel):
    listing_id: str = Field(..., description="Analiz edilmiş ilanın id'si")


class CoverLetterResponse(BaseModel):
    document_id: str
    listing_id: str
    company_name: str
    cover_letter_text: str
