"""Önyazı Ajanı: profil + ilan analizi + eşleştirme eksikleri -> kişiselleştirilmiş önyazı

Girdi olarak Analiz Ajanı (US-014) ve Eşleştirme Ajanı'nın (Sprint 2, henüz yazılmadı)
çıktılarını dict olarak alır - bu ajanların kendisi değil, sözleşmesi (contract) önemli,
böylece agent'lar birbirinden bağımsız test edilip sonra orkestratörde birleştirilebilir.
"""
import json
import re
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.prompt_safety import build_extra_prompt_section as _build_extra_prompt_section
from app.agents.strategy import STRATEGY_POTENTIAL as _STRATEGY_POTENTIAL
from app.agents.strategy import select_strategy as _select_strategy
from app.exceptions import ValidationException
from app.logging_config import get_logger
from app.models import Document
from app.observability import agent_run
from app.services.gemini_client import GeminiClient, get_gemini_client, render_prompt

logger = get_logger("cover_letter_agent")

TONE_DISPLAY_NAMES = {
    "professional": "profesyonel",
    "casual": "gündelik",
    "confident": "kendinden emin",
}

_MIN_WORDS = 250
_MAX_WORDS = 600

# Önceki önyazı prompt'a eklenirken taşmayı önlemek için (≈600 kelime + tampon)
_PREVIOUS_COVER_LETTER_MAX_LENGTH = 5000

# Panoya kopyalamaya hazır düz metin için - LLM markdown eklerse temizler
_MARKDOWN_ARTIFACTS = re.compile(r"[*_#`]+")
_FENCE = '"""'


def _sanitize(text: str) -> str:
    text = _MARKDOWN_ARTIFACTS.sub("", text)
    return text.strip()


def _build_previous_cover_letter_section(previous: Optional[str]) -> str:
    """Yeniden üretimde mevcut önyazıyı prompt'a güvenli şekilde ekler."""
    if not previous or not previous.strip():
        return ""
    text = previous.strip()[:_PREVIOUS_COVER_LETTER_MAX_LENGTH].replace(_FENCE, "'")
    return (
        "Bu ilan için daha önce üretilmiş önyazı aşağıda üç tırnak arasında verilmiştir. "
        "Yeniden yazarken bu metni GÖR ve temel al; güçlü kısımları koruyabilir, "
        "zayıf kısımları iyileştirebilirsin. Kullanıcının ekstra düzenleme notu varsa ona göre "
        "revize et. Önceki metni kelimesi kelimesine kopyalama; güncel profil, ilan ve "
        "eşleştirme bilgilerine uyumlu yeni bir önyazı üret:\n"
        f"{_FENCE}\n{text}\n{_FENCE}\n\n"
    )


async def _latest_cover_letter_text(
    db: AsyncSession,
    user_id: str,
    listing_id: Optional[str],
) -> Optional[str]:
    if not listing_id:
        return None
    result = await db.execute(
        select(Document)
        .where(
            Document.user_id == user_id,
            Document.listing_id == listing_id,
            Document.doc_type == "cover_letter",
        )
        .order_by(Document.created_at.desc(), Document.id.desc())
        .limit(1)
    )
    document = result.scalar_one_or_none()
    if document is None or not document.cover_letter_text:
        return None
    return document.cover_letter_text


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
        company_name: Optional[str] = None,
        extra_prompt: Optional[str] = None,
        previous_cover_letter: Optional[str] = None,
    ) -> str:
        if not user_profile or not job_analysis:
            raise ValidationException("user_profile ve job_analysis zorunludur")

        tone = TONE_DISPLAY_NAMES.get(tone_preference, TONE_DISPLAY_NAMES["professional"])
        strategy = _select_strategy(matching_gaps)
        low_score = strategy is _STRATEGY_POTENTIAL

        async with agent_run("cover_letter", tone=tone_preference):
            prompt = render_prompt(
                "cover_letter",
                tone=tone,
                company_name=company_name or "belirtilen şirket",
                user_profile=json.dumps(user_profile, ensure_ascii=False),
                job_analysis=json.dumps(job_analysis, ensure_ascii=False),
                matching_gaps=json.dumps(matching_gaps, ensure_ascii=False),
                strategy=strategy,
                previous_cover_letter_section=_build_previous_cover_letter_section(
                    previous_cover_letter
                ),
                extra_prompt_section=_build_extra_prompt_section(extra_prompt),
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

            logger.info(
                "cover_letter_generated",
                tone=tone_preference,
                word_count=word_count,
                score=matching_gaps.get("score"),
                low_score_strategy=low_score,
                extra_prompt_used=bool(extra_prompt),
                previous_cover_letter_used=bool(
                    previous_cover_letter and previous_cover_letter.strip()
                ),
            )
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
        company_name: Optional[str] = None,
        extra_prompt: Optional[str] = None,
        previous_cover_letter: Optional[str] = None,
    ) -> Document:
        """Önyazıyı üretir ve `documents` tablosuna kaydeder.

        previous_cover_letter verilmezse aynı ilan için en son kayıtlı önyazı
        otomatik yüklenir (yeniden üretimde agent eski metni görsün diye).
        """
        if previous_cover_letter is None:
            previous_cover_letter = await _latest_cover_letter_text(db, user_id, listing_id)

        text = await self.generate(
            user_profile,
            job_analysis,
            matching_gaps,
            tone_preference,
            company_name,
            extra_prompt=extra_prompt,
            previous_cover_letter=previous_cover_letter,
        )

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
