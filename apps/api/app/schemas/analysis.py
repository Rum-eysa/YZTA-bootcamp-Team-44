"""Analiz Ajanı endpoint şemaları"""
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    listing_text: str = Field(
        ..., min_length=1, max_length=20_000, description="İlan metni"
    )


class AnalyzeResponse(BaseModel):
    listing_id: str
    required_skills: list[str]
    nice_to_have: list[str]
    seniority: str
    position_title: str
    confidence: float
