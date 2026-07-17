"""Gemini API istemci wrapper'ı

Analiz/Eşleştirme/CV/Önyazı ajanlarının hepsi bu wrapper üzerinden Gemini'ye gider.
Sağlar: prompt template kaydı, yapılandırılmış (JSON) çıktı, token kullanım takibi,
rate limit + ücretsiz tier günlük kota izleme, hata yönetimi ve retry.
"""
import asyncio
import json
from typing import Any, Optional

import google.generativeai as genai
from app.config import settings
from app.exceptions import GeminiAPIException
from app.logging_config import get_logger
from google.api_core.exceptions import DeadlineExceeded, ResourceExhausted, ServiceUnavailable

logger = get_logger("gemini_client")

# Ücretsiz tier limitleri - GERÇEK ÖLÇÜLDÜ (1 Tem 2026): "gemini-flash-latest" bu
# hesapta gemini-3.5-flash'e çözülüyor ve günlük limit sadece 20 istek (Google'ın
# kendi 429 hata mesajından: "limit: 20, model: gemini-3.5-flash"). Fonksiyon
# çağrısı (generate_with_tools) round-trip başına ~2 gerçek API isteği tüketir
# (prompt + function-result), o yüzden quota_cost ile ayrı sayıyoruz.
FREE_TIER_RPM = 10
FREE_TIER_RPD = 18  # 20'nin altında güvenlik payı bırakıyoruz

# Hafıza katmanı (profil + geçmiş başvurular + ilan) context'e sığmalı. Gemini 1M token
# window iddia etse de pratikte 200k'nin üzerine çıkan promptlar maliyet/gecikme riski taşır.
MAX_CONTEXT_TOKENS = 200_000

_RETRYABLE_EXCEPTIONS = (ResourceExhausted, ServiceUnavailable, DeadlineExceeded)


# --- Prompt şablon kaydı -----------------------------------------------------
PROMPT_TEMPLATES: dict[str, str] = {
    "analyze_listing": (
        "Aşağıdaki iş ilanını analiz et ve gereksinimleri çıkar.\n\n"
        "İlan metni:\n{listing_text}\n\n"
        "required_skills, nice_to_have_skills, seniority ve position_title alanlarını "
        "içeren bir JSON döndür."
    ),
    "match_gap_analysis": (
        "Aday profili ile iş ilanı arasındaki uyumu analiz et.\n\n"
        "Aday: {user_profile}\n\nİlan gereksinimleri: {job_requirements}\n\n"
        "Hangi zorunlu becerilerin eşleştiğini, hangilerinin eksik olduğunu ve adayın "
        "bu iş için ne kadar hazır olduğunu JSON olarak döndür."
    ),
    "cover_letter": (
        "Aşağıdaki bilgilerle {tone} tonda, 300-500 kelimelik bir önyazı yaz.\n\n"
        "Başvurulan şirket: {company_name}\n"
        "Aday profili: {user_profile}\nİlan analizi: {job_analysis}\n"
        "Eşleştirme eksikleri: {matching_gaps}\n\n"
        "Strateji: {strategy}\n\n"
        "Kurallar:\n"
        "- Bu önyazı SADECE {company_name} için yazılıyor. Şirket adını en az bir kez "
        "açıkça geçir ve ilan analizindeki pozisyona/gereksinimlere özel referanslar ver.\n"
        "- Başka herhangi bir şirkete de gönderilebilecek genel/şablon ifadelerden kaçın; "
        "her cümle bu ilana ve bu şirkete özel olmalı.\n"
        "- Adayın eşleşen becerilerini somut örneklerle vurgula.\n"
        "- Eksik becerileri gizleme ama öğrenmeye açık/ilgili deneyimle telafi ederek yumuşat.\n"
        "- Panoya kopyalanıp doğrudan gönderilecek, o yüzden markdown, başlık, yıldız "
        "işareti kullanma - sadece düz metin, paragraflar halinde.\n"
        "- Sadece önyazı metnini döndür, açıklama veya giriş cümlesi ekleme."
    ),
}


def render_prompt(template_name: str, **kwargs: Any) -> str:
    """Kayıtlı bir prompt şablonunu değerlerle doldurur"""
    if template_name not in PROMPT_TEMPLATES:
        raise KeyError(f"Unknown prompt template: {template_name}")
    return PROMPT_TEMPLATES[template_name].format(**kwargs)


def estimate_tokens(text: str) -> int:
    """Kaba tahmin (~4 karakter/token) - context budget kontrolü için"""
    return len(text) // 4


class GeminiClient:
    """Gemini API için async, gözlemlenebilir, kota-korumalı istemci"""

    def __init__(self, model_name: Optional[str] = None):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = model_name or settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

    async def _check_quota(self, cost: int = 1) -> None:
        """Uygulama tarafı Redis kotası kapalı.

        Daha önce dakikalık/günlük ücretsiz tier koruması vardı; yerel geliştirme
        ve testleri engellediği için no-op bırakıldı. Google API'nin kendi
        limitleri hâlâ geçerli olabilir. cost parametresi geriye dönük uyumluluk
        için korunur."""
        return None

    def _check_context_budget(self, prompt: str) -> None:
        """Hafıza katmanından beslenen promptlar (profil+geçmiş+ilan) 200k token'ı
        aşarsa erken ve okunabilir bir hata veririz, ham API hatası yerine."""
        tokens = estimate_tokens(prompt)
        if tokens > MAX_CONTEXT_TOKENS:
            logger.warning("gemini_context_budget_exceeded", estimated_tokens=tokens)
            raise GeminiAPIException(
                f"Prompt too large for context window (~{tokens} tokens > {MAX_CONTEXT_TOKENS})"
            )
        if tokens > MAX_CONTEXT_TOKENS * 0.8:
            logger.warning("gemini_context_budget_near_limit", estimated_tokens=tokens)

    async def _generate_with_retry(
        self, prompt: str, generation_config: dict, max_retries: int = 3
    ):
        self._check_context_budget(prompt)
        await self._check_quota()

        delay = 1.0
        last_error: Optional[Exception] = None
        for attempt in range(1, max_retries + 1):
            try:
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    prompt,
                    generation_config=generation_config,
                )
                self._log_usage(response, attempt)
                return response
            except _RETRYABLE_EXCEPTIONS as exc:
                last_error = exc
                logger.warning(
                    "gemini_retryable_error",
                    attempt=attempt,
                    max_retries=max_retries,
                    error=str(exc),
                )
                if attempt < max_retries:
                    await asyncio.sleep(delay)
                    delay *= 2
            except Exception as exc:  # noqa: BLE001 - tüm Gemini hatalarını tekilleştiriyoruz
                logger.error("gemini_call_failed", error=str(exc))
                raise GeminiAPIException(f"Gemini API call failed: {exc}") from exc

        logger.error("gemini_retries_exhausted", error=str(last_error))
        raise GeminiAPIException("AI service unavailable after retries") from last_error

    def _log_usage(self, response, attempt: int) -> None:
        usage = getattr(response, "usage_metadata", None)
        logger.info(
            "gemini_call_completed",
            model=self.model_name,
            attempt=attempt,
            prompt_tokens=getattr(usage, "prompt_token_count", None),
            completion_tokens=getattr(usage, "candidates_token_count", None),
            total_tokens=getattr(usage, "total_token_count", None),
        )

    async def generate_text(self, prompt: str, temperature: float = 0.7) -> str:
        """Serbest metin üretimi (ör. önyazı)"""
        response = await self._generate_with_retry(
            prompt, generation_config={"temperature": temperature}
        )
        return response.text

    async def generate_json(
        self, prompt: str, response_schema: dict, temperature: float = 0.2
    ) -> dict:
        """Verilen JSON şemasına uyan yapılandırılmış çıktı üretir (Analiz/Eşleştirme ajanları)"""
        response = await self._generate_with_retry(
            prompt,
            generation_config={
                "temperature": temperature,
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            },
        )
        try:
            return json.loads(response.text)
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.error(
                "gemini_invalid_json",
                error=str(exc),
                raw=getattr(response, "text", None),
            )
            raise GeminiAPIException("AI returned malformed JSON") from exc

    async def generate_with_tools(self, prompt: str, tools: list) -> str:
        """Gerçek Gemini function calling: `tools`, docstring/type-hint'li Python
        fonksiyonlarından oluşur (ör. bir agent'ın DB sorgusu çalıştırması gibi).
        Gemini şemayı fonksiyonlardan kendisi çıkarır ve otomatik çağırır."""
        self._check_context_budget(prompt)
        await self._check_quota(cost=2)

        model = genai.GenerativeModel(self.model_name, tools=tools)
        chat = model.start_chat(enable_automatic_function_calling=True)

        try:
            response = await asyncio.to_thread(chat.send_message, prompt)
        except _RETRYABLE_EXCEPTIONS as exc:
            logger.warning("gemini_tools_retryable_error", error=str(exc))
            raise GeminiAPIException("AI service temporarily unavailable") from exc
        except Exception as exc:  # noqa: BLE001
            logger.error("gemini_tools_call_failed", error=str(exc))
            raise GeminiAPIException(f"Gemini function-calling call failed: {exc}") from exc

        self._log_usage(response, 1)
        return response.text


_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
