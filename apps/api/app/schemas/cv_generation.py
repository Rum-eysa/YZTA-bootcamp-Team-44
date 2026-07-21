"""CV Üretim Ajanı endpoint şemaları"""
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# US-050: CoverLetterRequest.extra_prompt ile aynı sınır (bkz. app/schemas/cover_letter.py)
EXTRA_PROMPT_MAX_LENGTH = 500


class CVGenerationRequest(BaseModel):
    listing_id: str = Field(..., description="Analiz edilmiş ilanın id'si")
    extra_prompt: Optional[str] = Field(
        default=None,
        max_length=EXTRA_PROMPT_MAX_LENGTH,
        description=(
            "İsteğe bağlı ekstra vurgu notu - verilirse CV Özet bölümü Gemini ile "
            "bu notu dikkate alarak yeniden yazılır (ör. düşük eşleşmede motivasyon "
            "vurgusu için)"
        ),
    )

    @field_validator("extra_prompt")
    @classmethod
    def _trim_extra_prompt(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None


class CVGenerationResponse(BaseModel):
    document_id: str
    listing_id: str
    cv_url: str
