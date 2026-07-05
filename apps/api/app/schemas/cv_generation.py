"""CV Üretim Ajanı endpoint şemaları"""
from pydantic import BaseModel, Field


class CVGenerationRequest(BaseModel):
    listing_id: str = Field(..., description="Analiz edilmiş ilanın id'si")


class CVGenerationResponse(BaseModel):
    document_id: str
    listing_id: str
    cv_url: str
