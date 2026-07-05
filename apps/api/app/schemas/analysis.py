"""Analiz Ajanı endpoint şemaları"""
from typing import Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    listing_text: str = Field(..., min_length=50, max_length=20_000, description="İlan metni")
    company_name: Optional[str] = Field(None, max_length=255, description="Başvurulan şirket adı")


class AnalyzeResponse(BaseModel):
    listing_id: str
    required_skills: list[str]
    nice_to_have: list[str]
    seniority: str
    position_title: str
    confidence: float
