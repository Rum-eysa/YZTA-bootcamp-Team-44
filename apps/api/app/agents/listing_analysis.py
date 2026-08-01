"""Analiz Ajanı: iş ilanı metnini yapılandırılmış JSON'a çevirir.

Gemini function calling kullanır - `extract_job_requirements` Python fonksiyonu tool
olarak verilir, Gemini şemayı fonksiyon imzasından çıkarır ve argümanları belirleyip
çağırır; biz çağrının argümanlarını yakalayıp sonucu döneriz.
"""
import re
from typing import Any, Optional

from app.exceptions import GeminiAPIException, ValidationException
from app.logging_config import get_logger
from app.observability import agent_run
from app.services.gemini_client import GeminiClient, get_gemini_client, render_prompt

logger = get_logger("listing_analysis_agent")

# Sayı + yıl/sene/year birimi ("5 yıl", "5+ yıl", "3 years", "2-4 yıl")
_DURATION_RE = re.compile(r"\d+\s*\+?\s*[-–]?\s*\d*\s*(?:yıl|yil|sene|yr|years?)", re.IGNORECASE)
# Deneyim/tecrübe/experience kelimeleri
_EXPERIENCE_WORD_RE = re.compile(r"deneyim|tecrübe|tecrube|experience", re.IGNORECASE)
# Süre/deneyim kalıbını temizleyip geriye somut beceri kalıp kalmadığına bakmak için
_STRIP_NOISE_RE = re.compile(
    r"\d+|\+|[-–]|yıl(?:lık)?|yil(?:lik)?|sene|yr|years?|deneyim\w*|tecrübe\w*|tecrube\w*"
    r"|experience|en az|en fazla|min\.?|max\.?|of|and|\bve\b",
    re.IGNORECASE,
)


def _is_experience_phrase(skill: str) -> bool:
    """Bir 'beceri' aslında somut bir teknik yetenek değil, süre/deneyim gereksinimi mi?
    (#99: Analiz Ajanı bazen '5+ yıl deneyim' gibi ifadeleri required_skills'e beceri
    olarak koyuyor; bunlar seniority'ye ait, beceri listesini kirletiyor.)

    Yalnızca geriye somut bir beceri kelimesi KALMAYAN saf süre/deneyim ifadelerini
    ayıklar - ör. '3+ yıl React deneyimi' düşürülmez (React korunur), '5 yıl deneyim'
    düşürülür."""
    text = (skill or "").strip().lower()
    if not text:
        return True
    if not (_DURATION_RE.search(text) or _EXPERIENCE_WORD_RE.search(text)):
        return False
    residual = _STRIP_NOISE_RE.sub(" ", text)
    residual = re.sub(r"[^\wçğıöşü]+", "", residual, flags=re.IGNORECASE)
    return len(residual) < 3


def _clean_skill_list(skills: list[str]) -> list[str]:
    """Süre/deneyim ifadelerini beceri listesinden ayıklar, kalanların sırasını korur."""
    return [s for s in skills if not _is_experience_phrase(s)]


class AnalyzeListingAgent:
    """İlan metnini yapılandırılmış JSON verisine çeviren analiz ajanı."""

    def __init__(self, client: Optional[GeminiClient] = None):
        self.client = client or get_gemini_client()

    async def analyze(self, listing_text: str) -> dict[str, Any]:
        if not listing_text or not listing_text.strip():
            raise ValidationException("listing_text boş olamaz")

        captured: dict[str, Any] = {}

        def extract_job_requirements(
            required_skills: list[str],
            nice_to_have_skills: list[str],
            seniority: str,
            position_title: str,
            confidence: float,
        ) -> str:
            """İş ilanından çıkarılan zorunlu beceriler, tercih edilen beceriler, kıdem
            seviyesi ve pozisyon başlığını kaydeder.

            Args:
                required_skills: İlanda zorunlu olarak istenen SOMUT teknik beceriler
                    (ör. "Python", "React", "PostgreSQL"). Deneyim süresi ifadelerini
                    (ör. "5+ yıl deneyim", "en az 3 yıl") buraya EKLEME - bunlar beceri
                    değildir, seniority alanına yansır.
                nice_to_have_skills: Tercih sebebi olarak belirtilen somut beceriler.
                    Yine deneyim süresi/yıl ifadeleri buraya girmez.
                seniority: junior, mid veya senior. İlandaki deneyim yılı/kıdem
                    ifadelerini burada değerlendir. Belirsizse en olası tahmini yap.
                position_title: İlandaki pozisyon başlığı.
                confidence: Çıkarımın ne kadar güvenilir olduğu, 0.0-1.0 arası.
                    İlan eksik/dağınık/belirsizse düşük bir değer ver (ör. 0.3-0.5).
            """
            # Gemini function calling argümanları protobuf RepeatedComposite tipinde
            # gelir (JSON serialize edilemez) - düz listeye çeviriyoruz. Ayrıca ikinci
            # bir savunma katmanı olarak süre/deneyim ifadelerini beceri listelerinden
            # deterministik olarak ayıklıyoruz (#99: LLM bunları bazen kaçırıyor).
            captured.update(
                {
                    "required_skills": _clean_skill_list(list(required_skills)),
                    "nice_to_have_skills": _clean_skill_list(list(nice_to_have_skills)),
                    "seniority": seniority,
                    "position_title": position_title,
                    "confidence": confidence,
                }
            )
            return "recorded"

        async with agent_run("listing_analysis"):
            from app.agents.prompt_safety import wrap_untrusted_block

            prompt = render_prompt(
                "analyze_listing",
                listing_text=wrap_untrusted_block("listing_text", listing_text),
            )
            await self.client.generate_with_tools(prompt, tools=[extract_job_requirements])

            if not captured:
                logger.warning("listing_analysis_empty_result", listing_preview=listing_text[:120])
                raise GeminiAPIException("Analiz ajanı ilan metninden veri çıkaramadı")

            logger.info(
                "listing_analysis_completed",
                position_title=captured.get("position_title"),
                seniority=captured.get("seniority"),
                confidence=captured.get("confidence"),
                required_skills_count=len(captured.get("required_skills") or []),
            )
            return captured


_agent: Optional[AnalyzeListingAgent] = None


def get_listing_analysis_agent() -> AnalyzeListingAgent:
    global _agent
    if _agent is None:
        _agent = AnalyzeListingAgent()
    return _agent
