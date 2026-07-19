"""Eşleştirme Ajanı testleri: skor formülü (saf Python) + semantik bonus (mock Gemini)"""
import json
import uuid
from unittest.mock import AsyncMock

import pytest
from app.agents.matching import MatchingAgent, calculate_exact_score, get_matching_agent
from app.exceptions import ValidationException
from app.models import JobListing, User


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


# --- Work experiences ve projects ile score breakdown testleri -----------------


def test_score_breakdown_includes_all_components():
    """Score breakdown'ın tüm bileşenleri içerdiğinden emin ol"""
    result = calculate_exact_score(
        user_skills=["Python", "FastAPI"],
        required_skills=["Python", "React"],
        nice_to_have_skills=["Docker"],
        user_seniority="mid",
        listing_seniority="mid",
    )

    assert "score_breakdown" in result
    assert "required" in result["score_breakdown"]
    assert "nice_to_have" in result["score_breakdown"]
    assert "seniority" in result["score_breakdown"]
    assert "semantic_bonus" in result["score_breakdown"]

    # required: 1/2*60=30, nice: 0/1*20=0, seniority: 20 -> 50
    assert result["score_breakdown"]["required"] == 30.0
    assert result["score_breakdown"]["nice_to_have"] == 0.0
    assert result["score_breakdown"]["seniority"] == 20.0
    assert result["score_breakdown"]["semantic_bonus"] == 0.0


def test_work_experiences_adds_to_skills():
    """Work experiences'ten beceri çıkarma testi"""
    result = calculate_exact_score(
        user_skills=["Python"],
        required_skills=["Python", "React"],
        nice_to_have_skills=[],
        user_seniority="mid",
        listing_seniority="mid",
        work_experiences=[
            {"title": "React Developer", "description": "React ile frontend geliştirme"},
        ],
    )

    # Work experiences'ten "react" kelimesi çıkılmalı
    assert "react" in result["matched_skills"]
    assert result["score_breakdown"]["required"] == 60.0  # 2/2*60


def test_projects_tech_stack_adds_to_skills():
    """Projects tech_stack'ten beceri çıkarma testi"""
    result = calculate_exact_score(
        user_skills=["Python"],
        required_skills=["Python", "Docker"],
        nice_to_have_skills=[],
        user_seniority="mid",
        listing_seniority="mid",
        projects=[
            {
                "title": "DevOps Project",
                "description": "CI/CD",
                "tech_stack": ["Docker", "Kubernetes"],
            },
        ],
    )

    # Projects tech_stack'ten "docker" kelimesi çıkılmalı
    assert "docker" in result["matched_skills"]
    assert result["score_breakdown"]["required"] == 60.0  # 2/2*60


def test_combined_work_and_projects_boost_score():
    """Work experiences ve projects birlikte skor artışı testi"""
    result = calculate_exact_score(
        user_skills=["Python"],
        required_skills=["Python", "React", "Docker"],
        nice_to_have_skills=["Kubernetes"],
        user_seniority="mid",
        listing_seniority="mid",
        work_experiences=[
            {"title": "React Developer", "description": "React ile frontend geliştirme"},
        ],
        projects=[
            {
                "title": "DevOps Project",
                "description": "CI/CD",
                "tech_stack": ["Docker", "Kubernetes"],
            },
        ],
    )

    # Tüm beceriler work/projects'ten gelmeli
    assert "react" in result["matched_skills"]
    assert "docker" in result["matched_skills"]
    assert "kubernetes" in result["matched_skills"]
    assert result["score_breakdown"]["required"] == 60.0  # 3/3*60
    assert result["score_breakdown"]["nice_to_have"] == 20.0  # 1/1*20
    assert result["score"] == 100.0


def test_projects_tech_stack_as_json_string_is_parsed():
    """tech_stack DB'den JSON string olarak gelebilir - liste gibi parse edilmeli"""
    result = calculate_exact_score(
        user_skills=["Python"],
        required_skills=["Python", "Docker"],
        nice_to_have_skills=[],
        user_seniority="mid",
        listing_seniority="mid",
        projects=[
            {"title": "DevOps", "description": "CI/CD", "tech_stack": json.dumps(["Docker"])},
        ],
    )

    assert "docker" in result["matched_skills"]


def test_projects_tech_stack_invalid_json_string_is_ignored():
    """tech_stack bozuk JSON string ise sessizce boş listeye düşmeli, çökmemeli"""
    result = calculate_exact_score(
        user_skills=["Python"],
        required_skills=["Python"],
        nice_to_have_skills=[],
        user_seniority="mid",
        listing_seniority="mid",
        projects=[
            {"title": "DevOps", "description": "", "tech_stack": "{not valid json"},
        ],
    )

    assert result["score"] == 100.0


def test_unknown_seniority_gets_neutral_score():
    """Seniority bilinmiyorsa (None veya tanınmayan string) ne tam puan ne sıfır - nötr 10 puan"""
    result = calculate_exact_score(
        user_skills=["Python"],
        required_skills=["Python"],
        nice_to_have_skills=[],
        user_seniority=None,
        listing_seniority="mid",
    )

    # required: 60, nice: 20, seniority: 10 (nötr) -> 90
    assert result["score"] == 90.0


@pytest.mark.asyncio
async def test_semantic_boost_empty_tool_call_returns_no_bonus():
    """Gemini function calling'i hiç çağırmazsa (captured boş kalırsa) bonus sıfır olmalı"""
    agent = MatchingAgent(client=FakeGeminiClient(fake_args=None))
    # generate_with_tools çağrılır ama tools[0] hiç invoke edilmez -> captured boş kalır
    agent.client.generate_with_tools = AsyncMock(return_value="ok")

    result = await agent.match(
        user_profile={"skills": ["Python"], "seniority": "mid"},
        job_analysis={
            "required_skills": ["Python", "React"],
            "nice_to_have_skills": [],
            "seniority": "mid",
        },
    )

    assert result["semantic_matches"] == []
    assert result["score_breakdown"]["semantic_bonus"] == 0.0


@pytest.mark.asyncio
async def test_semantic_boost_failure_falls_back_to_exact_score():
    """Gemini çağrısı hata verirse eşleştirme çökmemeli, deterministik skorla devam etmeli"""
    agent = MatchingAgent(client=FakeGeminiClient(fake_args=None))
    agent.client.generate_with_tools = AsyncMock(side_effect=RuntimeError("gemini down"))

    result = await agent.match(
        user_profile={"skills": ["Python"], "seniority": "mid"},
        job_analysis={
            "required_skills": ["Python", "React"],
            "nice_to_have_skills": [],
            "seniority": "mid",
        },
    )

    # required: 1/2*60=30 + nice 20 + seniority 20 = 70, bonus yok
    assert result["score"] == 70.0
    assert result["semantic_matches"] == []


@pytest.mark.asyncio
async def test_match_and_save_persists_match_row(test_session):
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email=f"matchagent-{user_id}@example.com", hashed_password="x")
    test_session.add(user)
    await test_session.commit()

    listing = JobListing(
        created_by=user_id,
        title="Backend Developer",
        raw_text="a" * 60,
        analysis_status="completed",
    )
    test_session.add(listing)
    await test_session.commit()
    await test_session.refresh(listing)

    agent = MatchingAgent(client=FakeGeminiClient(None))

    match = await agent.match_and_save(
        db=test_session,
        user_id=user_id,
        listing_id=listing.id,
        user_profile={"skills": ["Python"], "seniority": "mid"},
        job_analysis={"required_skills": ["Python"], "nice_to_have_skills": [], "seniority": "mid"},
    )

    assert match.id is not None
    assert match.user_id == user_id
    assert match.listing_id == listing.id
    assert match.score == 100.0


def test_get_matching_agent_returns_singleton():
    first = get_matching_agent()
    second = get_matching_agent()
    assert first is second


@pytest.mark.asyncio
async def test_match_includes_score_breakdown_in_result():
    """Match fonksiyonu sonucunda score_breakdown olmalı"""
    agent = MatchingAgent(client=FakeGeminiClient(None))

    result = await agent.match(
        user_profile={
            "skills": ["Python"],
            "seniority": "mid",
            "work_experiences": [{"title": "React Developer", "description": "React development"}],
            "projects": [],
        },
        job_analysis={
            "required_skills": ["Python", "React"],
            "nice_to_have_skills": [],
            "seniority": "mid",
        },
    )

    assert "score_breakdown" in result
    assert result["score_breakdown"]["required"] == 60.0
    assert result["score_breakdown"]["nice_to_have"] == 20.0
    assert result["score_breakdown"]["seniority"] == 20.0
    assert result["score_breakdown"]["semantic_bonus"] == 0.0
