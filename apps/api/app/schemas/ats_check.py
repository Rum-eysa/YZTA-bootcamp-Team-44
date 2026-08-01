"""Misafir ATS CV uyumluluk kontrolü yanıt şemaları."""
from typing import Literal

from pydantic import BaseModel, Field

AtsRating = Literal[
    "mukemmel",
    "iyi",
    "orta",
    "iyilestirilebilir",
    "iyilestirilmeli",
]


class AtsCategoryScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    rating: AtsRating
    feedback: str = ""


class AtsCheckResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    overall_rating: AtsRating
    categories: dict[str, AtsCategoryScore]
    summary: str = ""
    suggestions: list[str] = Field(default_factory=list)
