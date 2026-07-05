"""Analiz Ajanı: iş ilanı metnini yapılandırılmış JSON'a çevirir.

Gemini function calling kullanır - `extract_job_requirements` Python fonksiyonu tool
olarak verilir, Gemini şemayı fonksiyon imzasından çıkarır ve argümanları belirleyip
çağırır; biz çağrının argümanlarını yakalayıp sonucu döneriz.
"""
from typing import Any, Optional

from app.exceptions import GeminiAPIException, ValidationException
from app.logging_config import get_logger
from app.services.gemini_client import GeminiClient, get_gemini_client, render_prompt

logger = get_logger("listing_analysis_agent")


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
                required_skills: İlanda zorunlu olarak istenen teknik beceriler.
                nice_to_have_skills: Tercih sebebi olarak belirtilen beceriler.
                seniority: junior, mid veya senior. Belirsizse en olası tahmini yap.
                position_title: İlandaki pozisyon başlığı.
                confidence: Çıkarımın ne kadar güvenilir olduğu, 0.0-1.0 arası.
                    İlan eksik/dağınık/belirsizse düşük bir değer ver (ör. 0.3-0.5).
            """
            captured.update(
                {
                    # Gemini function calling argümanları protobuf RepeatedComposite
                    # tipinde gelir (JSON serialize edilemez) - düz listeye çeviriyoruz
                    "required_skills": list(required_skills),
                    "nice_to_have_skills": list(nice_to_have_skills),
                    "seniority": seniority,
                    "position_title": position_title,
                    "confidence": confidence,
                }
            )
            return "recorded"

        prompt = render_prompt("analyze_listing", listing_text=listing_text)
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
