"""Önyazı Ajanı endpoint şemaları"""
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# US-049: kullanıcının önyazıya eklemek istediği isteğe bağlı ekstra vurgu notu
# (ör. "takım çalışmasını vurgula"). Prompt'a taşınacağı için makul bir üst sınır var.
EXTRA_PROMPT_MAX_LENGTH = 500


class CoverLetterRequest(BaseModel):
    listing_id: str = Field(..., description="Analiz edilmiş ilanın id'si")
    extra_prompt: Optional[str] = Field(
        default=None,
        max_length=EXTRA_PROMPT_MAX_LENGTH,
        description="İsteğe bağlı ekstra vurgu notu (ör. 'takım çalışmasını vurgula')",
    )

    @field_validator("extra_prompt")
    @classmethod
    def _trim_extra_prompt(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None


class CoverLetterResponse(BaseModel):
    document_id: str
    listing_id: str
    company_name: str
    cover_letter_text: str
