"""Orkestratör: Ajan koordinasyonu + hafıza (US-030, retry/response düzeltmeleri US-041)

Tek giriş noktası: process(listing_text | listing_id, user_id)
Akış: Analiz -> Eşleştirme -> Önyazı -> CV

- Ajanlar arası bağlam ContextManager (US-017) üzerinden taşınır.
- Geçici (Gemini) hatalarında adım başına exponential backoff ile en fazla
  2 deneme yapılır (US-041): 1. deneme başarısızsa ~0.2s bekleyip 2. deneme
  yapılır, o da düşerse adım "failed" sayılır.
- Doküman adımları (önyazı/CV) kısmi başarısızlığa dayanıklıdır: biri düşerse
  akış devam eder, hata mesajı `errors[]`'e eklenir. Analiz ve eşleştirme ise
  zincirin temelidir - onlar düşerse akış durur (OrchestrationError).
- Her adımın süresi timeline olarak döner; token kullanımı zaten
  observability.agent_run + gemini_client loglarına düşer.
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any, Optional

from app.agents.cover_letter import CoverLetterAgent, get_cover_letter_agent
from app.agents.cv_generation import CVGenerationAgent, get_cv_generation_agent
from app.agents.listing_analysis import AnalyzeListingAgent, get_listing_analysis_agent
from app.agents.matching import MatchingAgent, get_matching_agent
from app.exceptions import GeminiAPIException, ValidationException
from app.logging_config import get_logger
from app.models import JobListing
from app.repositories.match import MatchRepository
from app.services.context import (
    ContextManager,
    job_analysis_from_context,
    matching_gaps_from_context,
    user_profile_for_agents,
    user_profile_for_matching,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("orchestrator")

_RETRYABLE = (GeminiAPIException,)
_MAX_ATTEMPTS = 2
_BASE_BACKOFF_SECONDS = 0.2


class OrchestrationError(Exception):
    """Zincirin temel adımı (analiz/eşleştirme) kurtarılamaz şekilde düştü"""

    def __init__(self, step: str, detail: str):
        self.step = step
        self.detail = detail
        super().__init__(f"{step}: {detail}")


class ApplicationOrchestrator:
    """Analiz -> Eşleştirme -> Önyazı -> CV zincirini koordine eder"""

    def __init__(
        self,
        analysis_agent: Optional[AnalyzeListingAgent] = None,
        matching_agent: Optional[MatchingAgent] = None,
        cover_letter_agent: Optional[CoverLetterAgent] = None,
        cv_agent: Optional[CVGenerationAgent] = None,
    ):
        self.analysis_agent = analysis_agent or get_listing_analysis_agent()
        self.matching_agent = matching_agent or get_matching_agent()
        self.cover_letter_agent = cover_letter_agent or get_cover_letter_agent()
        self.cv_agent = cv_agent or get_cv_generation_agent()

    async def _run_step(self, name: str, coro_factory, timeline: list[dict[str, Any]]):
        """Adımı çalıştırır, süresini ölçer; geçici hatada exponential backoff ile
        en fazla `_MAX_ATTEMPTS` kez dener (1. deneme dahil)."""
        started = time.monotonic()
        last_exc: Exception | None = None
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                result = await coro_factory()
                timeline.append(
                    {
                        "step": name,
                        "status": "completed",
                        "attempts": attempt,
                        "duration_ms": round((time.monotonic() - started) * 1000, 1),
                    }
                )
                return result
            except _RETRYABLE as exc:
                last_exc = exc
                if attempt < _MAX_ATTEMPTS:
                    backoff = _BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
                    logger.warning(
                        "orchestrator_step_retry", step=name, attempt=attempt, backoff_s=backoff
                    )
                    await asyncio.sleep(backoff)
            except Exception as exc:  # noqa: BLE001 - adım hatası timeline'a işlenir
                last_exc = exc
                break
        timeline.append(
            {
                "step": name,
                "status": "failed",
                "error": str(last_exc),
                "duration_ms": round((time.monotonic() - started) * 1000, 1),
            }
        )
        assert last_exc is not None
        raise last_exc  # çağıran karar verir: abort mu, devam mı

    async def process(
        self,
        db: AsyncSession,
        user_id: str,
        listing_text: Optional[str] = None,
        listing_id: Optional[str] = None,
        company_name: Optional[str] = None,
        generate_cover_letter: bool = True,
        generate_cv: bool = True,
    ) -> dict[str, Any]:
        if not listing_text and not listing_id:
            raise ValidationException("listing_text veya listing_id zorunludur")

        timeline: list[dict[str, Any]] = []
        errors: list[str] = []
        result: dict[str, Any] = {
            "timeline": timeline,
            "errors": errors,
            "cv_url": None,
            "cover_letter_text": None,
        }

        # 1) Analiz (yeni ilan metni geldiyse) --------------------------------
        if not listing_id:
            text: str = listing_text or ""
            try:
                analysis = await self._run_step(
                    "analysis", lambda: self.analysis_agent.analyze(text), timeline
                )
            except Exception as exc:
                raise OrchestrationError("analysis", str(exc)) from exc

            listing = JobListing(
                title=analysis.get("position_title"),
                company=company_name,
                raw_text=text,
                required_skills=json.dumps(
                    analysis.get("required_skills") or [], ensure_ascii=False
                ),
                nice_to_have_skills=json.dumps(
                    analysis.get("nice_to_have_skills") or [], ensure_ascii=False
                ),
                seniority=analysis.get("seniority"),
                parsed_json=json.dumps(analysis, ensure_ascii=False),
                analysis_status="completed",
                analyzed_at=datetime.now(timezone.utc),
                created_by=user_id,
            )
            db.add(listing)
            await db.commit()
            await db.refresh(listing)
            listing_id = listing.id
        result["listing_id"] = listing_id

        # 2) Bağlam yükle (hafıza katmanı) ------------------------------------
        context_manager = ContextManager(db)
        context = await context_manager.load(user_id, listing_id)
        result["analysis"] = job_analysis_from_context(context)

        # 3) Eşleştirme (cache'li) --------------------------------------------
        match_repo = MatchRepository(db)
        cached = await match_repo.get_by_user_and_listing(user_id, listing_id)
        if cached:
            timeline.append({"step": "matching", "status": "cached", "duration_ms": 0.0})
            match_data = {
                "score": cached.score,
                "matched_skills": json.loads(cached.matched_skills or "[]"),
                "missing_skills": json.loads(cached.missing_skills or "[]"),
            }
        else:
            try:
                match = await self._run_step(
                    "matching",
                    lambda: self.matching_agent.match_and_save(
                        db=db,
                        user_id=user_id,
                        listing_id=listing_id,
                        user_profile=user_profile_for_matching(context),
                        job_analysis=result["analysis"],
                    ),
                    timeline,
                )
            except Exception as exc:
                raise OrchestrationError("matching", str(exc)) from exc
            match_data = {
                "score": match.score,
                "matched_skills": json.loads(match.matched_skills or "[]"),
                "missing_skills": json.loads(match.missing_skills or "[]"),
            }
            # önyazı ajanı gaps'i context'ten okur - yeni match'i bağlama işle
            context = await context_manager.load(user_id, listing_id)
        result["match"] = match_data

        user_profile = user_profile_for_agents(context)
        job_analysis = result["analysis"]
        gaps = matching_gaps_from_context(context) or match_data
        tone = (context.get("user") or {}).get("tone_preference") or "professional"
        listing_company = (context.get("listing") or {}).get("company") or company_name

        # 4) Önyazı (kısmi başarısızlığa dayanıklı) ---------------------------
        if generate_cover_letter:
            try:
                document = await self._run_step(
                    "cover_letter",
                    lambda: self.cover_letter_agent.generate_and_save(
                        db=db,
                        user_id=user_id,
                        listing_id=listing_id,
                        user_profile=user_profile,
                        job_analysis=job_analysis,
                        matching_gaps=gaps,
                        tone_preference=tone,
                        company_name=listing_company,
                    ),
                    timeline,
                )
                result["cover_letter_text"] = document.cover_letter_text
            except Exception as exc:  # noqa: BLE001
                logger.warning("orchestrator_cover_letter_failed", error=str(exc))
                errors.append(f"cover_letter: {exc}")

        # 5) CV (kısmi başarısızlığa dayanıklı) -------------------------------
        if generate_cv:
            try:
                document = await self._run_step(
                    "cv",
                    lambda: self.cv_agent.generate_and_save(
                        db=db,
                        user_id=user_id,
                        listing_id=listing_id,
                        user_profile=user_profile,
                        job_analysis=job_analysis,
                    ),
                    timeline,
                )
                result["cv_url"] = document.cv_url
            except Exception as exc:  # noqa: BLE001
                logger.warning("orchestrator_cv_failed", error=str(exc))
                errors.append(f"cv: {exc}")

        logger.info(
            "orchestrator_completed",
            listing_id=listing_id,
            steps={s["step"]: s["status"] for s in timeline},
            error_count=len(errors),
        )
        return result


_orchestrator: Optional[ApplicationOrchestrator] = None


def get_orchestrator() -> ApplicationOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ApplicationOrchestrator()
    return _orchestrator
