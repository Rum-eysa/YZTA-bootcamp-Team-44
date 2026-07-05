"""Eşleştirme Ajanı: aday profili ile ilan arasındaki uyumu skorlar ve eksikleri bulur.

İki aşamalı çalışır:
1. Deterministik skor formülü (saf Python, LLM'siz) - test edilebilir, tekrarlanabilir.
2. Gemini function calling ile semantik boşluk analizi (ör. "Vue.js" bilen adayın
   "React" isteyen ilana ne kadar yakın olduğu gibi tam string eşleşmesiyle
   yakalanamayacak durumlar) - skoru küçük bir bonusla besler, ana formülü ezmez.

Skor formülü:
- Zorunlu beceriler eşleşmesi: max 60 puan
- Nice-to-have beceriler eşleşmesi: max 20 puan
- Seniority uyumu: max 20 puan (tam eşleşme=20, bir seviye fark=10, iki seviye fark=0)
- Semantik bonus (Gemini): max 100'ü aşmayacak şekilde +0-10 puan
"""
import json
from typing import Any, Optional

from app.exceptions import ValidationException
from app.logging_config import get_logger
from app.models import Match
from app.services.gemini_client import GeminiClient, get_gemini_client, render_prompt
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("matching_agent")

SENIORITY_ORDER = {"junior": 0, "mid": 1, "senior": 2}


def _normalize(skills: list[str]) -> set[str]:
    return {s.strip().lower() for s in skills if s and s.strip()}


def calculate_exact_score(
    user_skills: list[str],
    required_skills: list[str],
    nice_to_have_skills: list[str],
    user_seniority: Optional[str],
    listing_seniority: Optional[str],
) -> dict[str, Any]:
    """Saf Python skor hesaplama - deterministik, LLM'siz, test edilebilir"""
    user_set = _normalize(user_skills)
    required_set = _normalize(required_skills)
    nice_set = _normalize(nice_to_have_skills)

    matched_required = required_set & user_set
    missing_required = required_set - user_set
    matched_nice = nice_set & user_set

    required_score = (len(matched_required) / len(required_set)) * 60 if required_set else 60.0
    nice_score = (len(matched_nice) / len(nice_set)) * 20 if nice_set else 20.0

    user_level = SENIORITY_ORDER.get((user_seniority or "").lower())
    listing_level = SENIORITY_ORDER.get((listing_seniority or "").lower())
    if user_level is None or listing_level is None:
        seniority_score = 10.0  # bilinmiyorsa ne tam puan ne sıfır - nötr
    else:
        distance = abs(user_level - listing_level)
        seniority_score = {0: 20.0, 1: 10.0}.get(distance, 0.0)

    score = round(required_score + nice_score + seniority_score, 1)

    return {
        "score": min(score, 100.0),
        "matched_skills": sorted(matched_required | matched_nice),
        "missing_skills": sorted(missing_required),
    }


class MatchingAgent:
    def __init__(self, client: Optional[GeminiClient] = None):
        self.client = client or get_gemini_client()

    async def _semantic_boost(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        missing_skills: list[str],
    ) -> dict[str, Any]:
        """Eksik görünen becerilerde semantik yakınlık var mı (Gemini function calling)"""
        if not missing_skills:
            return {"bonus": 0.0, "readiness_summary": "", "semantic_matches": []}

        captured: dict[str, Any] = {}

        def record_match_analysis(
            readiness_summary: str,
            semantic_near_matches: list[str],
            bonus_points: float,
        ) -> str:
            """Adayın ilana ne kadar hazır olduğunu ve tam string eşleşmesiyle
            yakalanamayan ama yakın/eşdeğer becerileri kaydeder.

            Args:
                readiness_summary: Adayın bu iş için ne kadar hazır olduğuna dair
                    1-2 cümlelik özet.
                semantic_near_matches: Eksik görünen ama adayın yakın/eşdeğer bir
                    beceriye sahip olduğu durumlar (ör. "React yerine Vue.js biliyor").
                bonus_points: semantic_near_matches nedeniyle verilecek bonus puan,
                    0-10 arası, her yakın eşleşme için ~2-3 puan makuldür.
            """
            captured.update(
                {
                    "readiness_summary": readiness_summary,
                    # Gemini function calling argümanları protobuf RepeatedComposite
                    # tipinde gelir (JSON serialize edilemez) - düz listeye çeviriyoruz
                    "semantic_matches": list(semantic_near_matches),
                    "bonus": max(0.0, min(bonus_points, 10.0)),
                }
            )
            return "recorded"

        prompt = render_prompt(
            "match_gap_analysis",
            user_profile=json.dumps(user_profile, ensure_ascii=False),
            job_requirements=json.dumps(
                {**job_analysis, "missing_skills": missing_skills}, ensure_ascii=False
            ),
        )
        await self.client.generate_with_tools(prompt, tools=[record_match_analysis])

        if not captured:
            logger.warning("matching_semantic_boost_empty")
            return {"bonus": 0.0, "readiness_summary": "", "semantic_matches": []}
        return captured

    async def match(
        self, user_profile: dict[str, Any], job_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        if not user_profile or not job_analysis:
            raise ValidationException("user_profile ve job_analysis zorunludur")

        exact = calculate_exact_score(
            user_skills=user_profile.get("skills") or [],
            required_skills=job_analysis.get("required_skills") or [],
            nice_to_have_skills=job_analysis.get("nice_to_have_skills") or [],
            user_seniority=user_profile.get("seniority"),
            listing_seniority=job_analysis.get("seniority"),
        )

        semantic = await self._semantic_boost(user_profile, job_analysis, exact["missing_skills"])

        final_score = min(round(exact["score"] + semantic["bonus"], 1), 100.0)

        result = {
            "score": final_score,
            "matched_skills": exact["matched_skills"],
            "missing_skills": exact["missing_skills"],
            "readiness_summary": semantic["readiness_summary"],
            "semantic_matches": semantic["semantic_matches"],
        }

        logger.info(
            "matching_completed",
            score=final_score,
            matched_count=len(exact["matched_skills"]),
            missing_count=len(exact["missing_skills"]),
        )
        return result

    async def match_and_save(
        self,
        db: AsyncSession,
        user_id: str,
        listing_id: str,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
    ) -> Match:
        result = await self.match(user_profile, job_analysis)

        match = Match(
            user_id=user_id,
            listing_id=listing_id,
            score=result["score"],
            matched_skills=json.dumps(result["matched_skills"], ensure_ascii=False),
            missing_skills=json.dumps(result["missing_skills"], ensure_ascii=False),
        )
        db.add(match)
        await db.commit()
        await db.refresh(match)
        return match


_agent: Optional[MatchingAgent] = None


def get_matching_agent() -> MatchingAgent:
    global _agent
    if _agent is None:
        _agent = MatchingAgent()
    return _agent
