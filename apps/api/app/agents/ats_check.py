"""ATS CV uyumluluk ajanı: PDF metnini çıkarır, heuristic sinyaller + Gemini ile skorlar."""
from __future__ import annotations

import re
from datetime import date
from io import BytesIO
from typing import Any, Optional

from app.agents.prompt_safety import wrap_untrusted_block
from app.exceptions import GeminiAPIException, ValidationException
from app.logging_config import get_logger
from app.observability import agent_run
from app.services.careertrack_pdf import is_careertrack_pdf
from app.services.gemini_client import GeminiClient, get_gemini_client
from pypdf import PdfReader
from pypdf.errors import PdfReadError

logger = get_logger("ats_check_agent")

RATING_KEYS = (
    "mukemmel",
    "iyi",
    "orta",
    "iyilestirilebilir",
    "iyilestirilmeli",
)

CATEGORY_KEYS = ("tasarim", "duzen", "icerik")

_SECTION_PATTERNS = [
    r"\b(experience|deneyim|iş deneyimi|work experience)\b",
    r"\b(education|eğitim|öğrenim)\b",
    r"\b(skills|beceriler|yetenekler)\b",
    r"\b(projects?|projeler?)\b",
    r"\b(summary|özet|about|hakkımda|profil)\b",
    r"\b(contact|iletişim)\b",
]

_CATEGORY_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "score": {"type": "INTEGER"},
        "feedback": {"type": "STRING"},
    },
    "required": ["score", "feedback"],
}

ATS_CHECK_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "tasarim": _CATEGORY_SCHEMA,
        "duzen": _CATEGORY_SCHEMA,
        "icerik": _CATEGORY_SCHEMA,
        "summary": {"type": "STRING"},
        "suggestions": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["tasarim", "duzen", "icerik", "summary", "suggestions"],
}


def score_to_rating(score: int) -> str:
    if score >= 90:
        return "mukemmel"
    if score >= 75:
        return "iyi"
    if score >= 55:
        return "orta"
    if score >= 35:
        return "iyilestirilebilir"
    return "iyilestirilmeli"


def _clamp_score(value: Any) -> int:
    try:
        n = int(round(float(value)))
    except (TypeError, ValueError):
        n = 0
    return max(0, min(100, n))


def extract_pdf_text(pdf_bytes: bytes) -> tuple[str, int]:
    """PDF'den metin ve sayfa sayısı çıkarır."""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
    except PdfReadError as exc:
        raise ValidationException("PDF okunamadı. Geçerli bir PDF yükleyin.") from exc

    pages = len(reader.pages)
    if pages < 1:
        raise ValidationException("PDF en az bir sayfa içermelidir.")

    parts: list[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:  # noqa: BLE001
            continue
    text = "\n".join(parts).strip()
    if len(text) < 40:
        raise ValidationException(
            "PDF'den yeterli metin çıkarılamadı. ATS için metin seçilebilir bir CV yükleyin."
        )
    return text, pages


def collect_heuristics(text: str, page_count: int) -> dict[str, Any]:
    """ATS için hızlı, deterministik ön-sinyaller."""
    lower = text.lower()
    email = bool(re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I))
    phone = bool(re.search(r"(\+?\d[\d\s().-]{7,}\d)", text))
    sections = [
        name
        for name, pat in zip(
            ["experience", "education", "skills", "projects", "summary", "contact"],
            _SECTION_PATTERNS,
            strict=True,
        )
        if re.search(pat, lower, re.I)
    ]
    special_ratio = sum(1 for c in text if ord(c) > 127 and not c.isalpha()) / max(len(text), 1)
    bullet_like = len(re.findall(r"(^|\n)\s*[•\-\*▪‣]\s+\S", text))
    return {
        "page_count": page_count,
        "char_count": len(text),
        "has_email": email,
        "has_phone": phone,
        "detected_sections": sections,
        "special_char_ratio": round(special_ratio, 4),
        "bullet_like_lines": bullet_like,
    }


def _normalize_category(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {}
    score = _clamp_score(raw.get("score", 0))
    feedback = str(raw.get("feedback") or "").strip()
    return {
        "score": score,
        "rating": score_to_rating(score),
        "feedback": feedback,
    }


def normalize_ats_result(raw: dict[str, Any], *, careertrack_cv: bool = False) -> dict[str, Any]:
    categories = {key: _normalize_category(raw.get(key)) for key in CATEGORY_KEYS}
    if careertrack_cv:
        # Platformun ürettiği ATS şablonları tasarım ve düzende mükemmel sayılır
        for key in ("tasarim", "duzen"):
            prev = categories[key]
            categories[key] = {
                "score": 100,
                "rating": "mukemmel",
                "feedback": prev.get("feedback")
                or "CareerTrack ATS şablonu: tek sütun, standart font ve temiz düzen.",
            }
    scores = [categories[k]["score"] for k in CATEGORY_KEYS]
    overall = int(round(sum(scores) / len(scores))) if scores else 0
    suggestions = raw.get("suggestions") or []
    if not isinstance(suggestions, list):
        suggestions = []
    clean_suggestions = [str(s).strip() for s in suggestions if str(s).strip()][:6]
    if careertrack_cv:
        clean_suggestions = [
            s
            for s in clean_suggestions
            if not re.search(r"tasar[ıi]m|d[üu]zen|s[üu]tun|font|layout", s, re.I)
        ]
    return {
        "overall_score": overall,
        "overall_rating": score_to_rating(overall),
        "categories": categories,
        "summary": str(raw.get("summary") or "").strip(),
        "suggestions": clean_suggestions,
    }


class AtsCheckAgent:
    def __init__(self, client: Optional[GeminiClient] = None):
        self.client = client or get_gemini_client()

    async def analyze(self, pdf_bytes: bytes) -> dict[str, Any]:
        text, page_count = extract_pdf_text(pdf_bytes)
        heuristics = collect_heuristics(text, page_count)

        careertrack_cv = is_careertrack_pdf(pdf_bytes)
        today = date.today()
        prompt = (
            "Sen bir ATS (Applicant Tracking System) CV uyumluluk uzmanısın. "
            "Adayın yüklediği CV metnini ve heuristic sinyalleri kullanarak "
            "üç kategoride 0-100 arası puan ver.\n\n"
            f"BUGÜNÜN TARİHİ: {today.isoformat()} (yıl={today.year}). "
            "Tarihleri değerlendirirken bu tarihi referans al. "
            f"{today.year} yılı veya daha önceki tarihler gelecek tarih DEĞİLDİR. "
            f"Yalnızca {today.year}'dan sonraki yılları (ör. {today.year + 1}+) "
            "geleceğe dönük / hatalı tarih say. "
            f"Sertifika, eğitim veya deneyimde {today.year} geçiyorsa bunu hata olarak "
            "işaretleme ve öneri olarak yazma.\n\n"
            "Kategoriler:\n"
            "- tasarim: ATS dostu görsel yapı (tek sütun tercihi, grafik/ikon/tablo riski, "
            "özel karakter/font riski, görsel CV şablonları).\n"
            "- duzen: Bölüm sırası, okunabilirlik, boşluklar, başlık tutarlılığı, "
            "sayfa uzunluğu (tercihen 1-2 sayfa).\n"
            "- icerik: İletişim bilgisi, net bölümler, eylem fiilleri, somut başarılar, "
            "anahtar kelime yoğunluğu, eksik kritik alanlar.\n\n"
            "Kurallar:\n"
            "- Skorlar tamsayı 0-100 olmalı.\n"
            "- Tek sütunlu, standart fontlu, metin seçilebilir, 1-2 sayfalık ATS odaklı "
            "şablonlar tasarim ve duzen kategorilerinde 95-100 almalıdır.\n"
            "- Her kategori için kısa Türkçe feedback yaz.\n"
            "- summary kısa Türkçe genel özet olsun.\n"
            "- suggestions en fazla 5 somut iyileştirme maddesi olsun.\n"
            "- Uydurma kişisel bilgi ekleme; yalnızca verilen metne dayan.\n\n"
            f"CareerTrack üretilmiş CV: {careertrack_cv}\n"
            f"Heuristic sinyaller (JSON benzeri):\n{heuristics}\n\n"
            f"{wrap_untrusted_block('cv_text', text)}\n"
        )

        async with agent_run("ats_check"):
            try:
                raw = await self.client.generate_json(
                    prompt,
                    response_schema=ATS_CHECK_SCHEMA,
                    temperature=0.2,
                )
            except GeminiAPIException:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.error("ats_check_gemini_failed", error=str(exc))
                raise GeminiAPIException("ATS analizi şu an yapılamıyor") from exc

        result = normalize_ats_result(
            raw if isinstance(raw, dict) else {},
            careertrack_cv=careertrack_cv,
        )
        logger.info(
            "ats_check_completed",
            overall_score=result["overall_score"],
            page_count=page_count,
            sections=heuristics["detected_sections"],
            careertrack_cv=careertrack_cv,
        )
        return result


_agent: Optional[AtsCheckAgent] = None


def get_ats_check_agent() -> AtsCheckAgent:
    global _agent
    if _agent is None:
        _agent = AtsCheckAgent()
    return _agent
