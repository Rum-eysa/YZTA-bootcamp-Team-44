"""Önyazı Ajanı: profil + ilan analizi + eşleştirme eksikleri -> kişiselleştirilmiş önyazı

Girdi olarak Analiz Ajanı (US-014) ve Eşleştirme Ajanı'nın (Sprint 2, henüz yazılmadı)
çıktılarını dict olarak alır - bu ajanların kendisi değil, sözleşmesi (contract) önemli,
böylece agent'lar birbirinden bağımsız test edilip sonra orkestratörde birleştirilebilir.
"""
import json
import re
from typing import Any, Optional

from app.exceptions import ValidationException
from app.logging_config import get_logger
from app.models import Document
from app.services.gemini_client import GeminiClient, get_gemini_client, render_prompt
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("cover_letter_agent")

TONE_DISPLAY_NAMES = {
    "professional": "profesyonel",
    "casual": "gündelik",
    "confident": "kendinden emin",
}

_MIN_WORDS = 250
_MAX_WORDS = 600

# Panoya kopyalamaya hazır düz metin için - LLM markdown eklerse temizler
_MARKDOWN_ARTIFACTS = re.compile(r"[*_#`]+")


def _sanitize(text: str) -> str:
    text = _MARKDOWN_ARTIFACTS.sub("", text)
    return text.strip()


class CoverLetterAgent:
    """user_profile + job_analysis + matching_gaps -> ~300-500 kelimelik düz metin önyazı"""

    def __init__(self, client: Optional[GeminiClient] = None):
        self.client = client or get_gemini_client()

    async def generate(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        matching_gaps: dict[str, Any],
        tone_preference: str = "professional",
    ) -> str:
        if not user_profile or not job_analysis:
            raise ValidationException("user_profile ve job_analysis zorunludur")

        tone = TONE_DISPLAY_NAMES.get(tone_preference, TONE_DISPLAY_NAMES["professional"])

        prompt = render_prompt(
            "cover_letter",
            tone=tone,
            user_profile=json.dumps(user_profile, ensure_ascii=False),
            job_analysis=json.dumps(job_analysis, ensure_ascii=False),
            matching_gaps=json.dumps(matching_gaps, ensure_ascii=False),
        )

        raw_text = await self.client.generate_text(prompt, temperature=0.7)
        text = _sanitize(raw_text)
        word_count = len(text.split())

        if word_count < _MIN_WORDS or word_count > _MAX_WORDS:
            logger.warning(
                "cover_letter_word_count_out_of_range",
                word_count=word_count,
                tone=tone_preference,
            )

        logger.info("cover_letter_generated", tone=tone_preference, word_count=word_count)
        return text

    async def generate_and_save(
        self,
        db: AsyncSession,
        user_id: str,
        listing_id: Optional[str],
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        matching_gaps: dict[str, Any],
        tone_preference: str = "professional",
    ) -> Document:
        """Önyazıyı üretir ve `documents` tablosuna kaydeder"""
        text = await self.generate(user_profile, job_analysis, matching_gaps, tone_preference)

        document = Document(
            user_id=user_id,
            listing_id=listing_id,
            doc_type="cover_letter",
            cover_letter_text=text,
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document


_agent: Optional[CoverLetterAgent] = None


def get_cover_letter_agent() -> CoverLetterAgent:
    global _agent
    if _agent is None:
        _agent = CoverLetterAgent()
    return _agent
