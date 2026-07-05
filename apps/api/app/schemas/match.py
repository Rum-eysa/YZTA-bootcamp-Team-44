"""Eşleştirme Ajanı endpoint şemaları"""
from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    listing_id: str = Field(..., description="Eşleştirilecek ilanın id'si")


class MatchResponse(BaseModel):
    match_id: str
    listing_id: str
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    cached: bool
