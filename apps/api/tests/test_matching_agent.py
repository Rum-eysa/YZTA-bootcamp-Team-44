"""Eşleştirme Ajanı testleri: skor formülü (saf Python) + semantik bonus (mock Gemini)"""
from unittest.mock import AsyncMock

import pytest

from app.agents.matching import MatchingAgent, calculate_exact_score
from app.exceptions import ValidationException


class FakeGeminiClient:
    """generate_with_tools çağrısını simüle eder"""

    def __init__(self, fake_args: dict | None):
        self.fake_args = fake_args
        self.generate_with_tools = AsyncMock(side_effect=self._call_tool)

    async def _call_tool(self, prompt: str, tools: list):
        if self.fake_args is not None:
            tools[0](**self.fake_args)
        return "ok"


# --- Saf Python skor formülü testleri (deterministik, LLM'siz) -----------------


def test_perfect_match_scores_100():
    result = calculate_exact_score(
        user_skills=["Python", "FastAPI", "Docker"],
        required_skills=["Python", "FastAPI"],
        nice_to_have_skills=["Docker"],
        user_seniority="mid",
        listing_seniority="mid",
    )
    assert result["score"] == 100.0
    assert result["missing_skills"] == []


def test_missing_required_skill_lowers_score():
    result = calculate_exact_score(
        user_skills=["Python"],
        required_skills=["Python", "FastAPI"],
        nice_to_have_skills=[],
        user_seniority="mid",
        listing_seniority="mid",
    )
    # required: 1/2*60=30, nice: (bos)=20, seniority: tam eslesme=20 -> 70
    assert result["score"] == 70.0
    assert result["missing_skills"] == ["fastapi"]


def test_seniority_two_levels_apart_scores_zero_bonus():
    result = calculate_exact_score(
        user_skills=["Python"],
        required_skills=["Python"],
        nice_to_have_skills=[],
        user_seniority="junior",
        listing_seniority="senior",
    )
    # required: 60, nice: 20, seniority: 2 seviye fark=0 -> 80
    assert result["score"] == 80.0


def test_case_insensitive_skill_matching():
    result = calculate_exact_score(
        user_skills=["python", "FASTAPI"],
        required_skills=["Python", "FastAPI"],
        nice_to_have_skills=[],
        user_seniority="mid",
        listing_seniority="mid",
    )
    assert result["score"] == 100.0


def test_no_required_skills_listed_gives_full_required_score():
    """İlan hiç zorunlu beceri belirtmemişse (Analiz Ajanı boş döndüyse) 0'a bölme hatası olmamalı"""
    result = calculate_exact_score(
        user_skills=["Python"],
        required_skills=[],
        nice_to_have_skills=[],
        user_seniority="mid",
        listing_seniority="mid",
    )
    assert result["score"] == 100.0


# --- Ajan (semantik bonus dahil) testleri --------------------------------------


@pytest.mark.asyncio
async def test_match_combines_exact_and_semantic_bonus():
    fake_semantic = {
        "readiness_summary": "Aday büyük ölçüde hazır.",
        "semantic_near_matches": ["Vue.js -> React'e yakın"],
        "bonus_points": 5.0,
    }
    agent = MatchingAgent(client=FakeGeminiClient(fake_semantic))

    result = await agent.match(
        user_profile={"skills": ["Python"], "seniority": "mid"},
        job_analysis={
            "required_skills": ["Python", "React"],
            "nice_to_have_skills": [],
            "seniority": "mid",
        },
    )

    # exact: required 1/2*60=30 + nice 20 + seniority 20 = 70, +5 bonus = 75
    assert result["score"] == 75.0
    assert result["missing_skills"] == ["react"]
    assert "semantic_near_matches" not in result  # anahtar adı normalize edilmiş olmalı
    assert result["semantic_matches"] == ["Vue.js -> React'e yakın"]


@pytest.mark.asyncio
async def test_match_score_never_exceeds_100():
    fake_semantic = {
        "readiness_summary": "Tam hazır.",
        "semantic_near_matches": ["x"],
        "bonus_points": 10.0,
    }
    agent = MatchingAgent(client=FakeGeminiClient(fake_semantic))

    result = await agent.match(
        user_profile={"skills": ["Python", "FastAPI"], "seniority": "mid"},
        job_analysis={
            "required_skills": ["Python", "FastAPI"],
            "nice_to_have_skills": [],
            "seniority": "mid",
        },
    )

    assert result["score"] == 100.0


@pytest.mark.asyncio
async def test_no_missing_skills_skips_gemini_call():
    """Eksik beceri yoksa semantik bonus için Gemini'ye hiç gidilmemeli (gereksiz maliyet)"""
    client = FakeGeminiClient(None)
    agent = MatchingAgent(client=client)

    result = await agent.match(
        user_profile={"skills": ["Python"], "seniority": "mid"},
        job_analysis={
            "required_skills": ["Python"],
            "nice_to_have_skills": [],
            "seniority": "mid",
        },
    )

    client.generate_with_tools.assert_not_called()
    assert result["score"] == 100.0


@pytest.mark.asyncio
async def test_missing_profile_raises_validation_error():
    agent = MatchingAgent(client=FakeGeminiClient(None))

    with pytest.raises(ValidationException):
        await agent.match({}, {"required_skills": ["Python"]})
