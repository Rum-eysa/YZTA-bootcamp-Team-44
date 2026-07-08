"""Eşleştirme Ajanı endpoint şemaları"""
from typing import Optional
from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    listing_id: str = Field(..., description="Eşleştirilecek ilanın id'si")


class ScoreBreakdown(BaseModel):
    required: float
    nice_to_have: float
    seniority: float
    semantic_bonus: float


class MatchResponse(BaseModel):
    match_id: str
    listing_id: str
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    score_breakdown: Optional[ScoreBreakdown] = None
    cached: bool
