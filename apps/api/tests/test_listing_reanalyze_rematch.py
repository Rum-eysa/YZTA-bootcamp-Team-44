"""US-037: İlan güncelle -> yeniden analiz et -> eşleşmeyi güncelle akışı

Mock Gemini (StubAnalysisAgent/StubMatchingAgent), gerçek HTTP + JWT + DB.
"""
import json
import uuid

import pytest
from app.agents.listing_analysis import get_listing_analysis_agent
from app.agents.matching import get_matching_agent
from app.main import app
from app.models import JobListing, Match, User
from httpx import AsyncClient
from sqlalchemy import select

INITIAL_TEXT = (
    "Acme Yazılım A.Ş. Backend Developer arıyor. Zorunlu: Python, FastAPI. "
    "Tercih sebebi: Docker."
)
UPDATED_TEXT = (
    "Acme Yazılım A.Ş. Backend Developer arıyor. Zorunlu: Python, FastAPI, "
    "Kubernetes. Tercih sebebi: Docker, AWS. (güncellendi)"
)

INITIAL_ANALYSIS = {
    "position_title": "Backend Developer",
    "required_skills": ["Python", "FastAPI"],
    "nice_to_have_skills": ["Docker"],
    "seniority": "junior",
    "confidence": 0.9,
}
UPDATED_ANALYSIS = {
    "position_title": "Backend Developer",
    "required_skills": ["Python", "FastAPI", "Kubernetes"],
    "nice_to_have_skills": ["Docker", "AWS"],
    "seniority": "mid",
    "confidence": 0.93,
}


class StubAnalysisAgent:
    """Her çağrıda listing_text'e göre farklı analiz döner - metin değişikliğini simüle eder"""

    async def analyze(self, listing_text: str):
        if "Kubernetes" in listing_text:
            return dict(UPDATED_ANALYSIS)
        return dict(INITIAL_ANALYSIS)


class StubMatchingAgent:
    def __init__(self):
        self.calls = 0

    async def match_and_save(self, db, user_id, listing_id, user_profile, job_analysis):
        self.calls += 1
        # Skor, çağrı sayısına göre değişsin ki "yeniden hesaplandı" ayırt edilebilsin
        score = 60.0 if self.calls == 1 else 85.0
        match = Match(
            user_id=user_id,
            listing_id=listing_id,
            score=score,
            matched_skills=json.dumps(job_analysis.get("required_skills") or []),
            missing_skills=json.dumps([]),
        )
        db.add(match)
        await db.commit()
        await db.refresh(match)
        return match


@pytest.fixture(autouse=True)
def _stub_agents():
    stub_analysis = StubAnalysisAgent()
    stub_matching = StubMatchingAgent()
    app.dependency_overrides[get_listing_analysis_agent] = lambda: stub_analysis
    app.dependency_overrides[get_matching_agent] = lambda: stub_matching
    yield
    app.dependency_overrides.pop(get_listing_analysis_agent, None)
    app.dependency_overrides.pop(get_matching_agent, None)


async def _register_and_login(client: AsyncClient) -> dict:
    email = f"us037-{uuid.uuid4()}@example.com"
    await client.post(
        "/api/auth/register",
        json={"email": email, "password": "TestPass123", "full_name": "Test User"},
    )
    login = await client.post("/api/auth/login", json={"email": email, "password": "TestPass123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_update_reanalyze_rematch_flow(client: AsyncClient, test_session):
    """Tam akış: ilan analiz et -> güncelle -> yeniden analiz et -> eşleşmeyi güncelle"""
    headers = await _register_and_login(client)

    # 1) İlk analiz
    analyze = await client.post(
        "/api/analyze",
        headers=headers,
        json={"listing_text": INITIAL_TEXT, "company_name": "Acme"},
    )
    assert analyze.status_code == 200
    listing_id = analyze.json()["listing_id"]
    assert analyze.json()["required_skills"] == ["Python", "FastAPI"]

    # 2) İlk eşleştirme (cache'e yazılır)
    match1 = await client.post("/api/match", headers=headers, json={"listing_id": listing_id})
    assert match1.status_code == 200
    assert match1.json()["score"] == 60.0

    # 3) İlanı güncelle (raw_text değişti)
    update = await client.patch(
        f"/api/listings/{listing_id}",
        headers=headers,
        json={"raw_text": UPDATED_TEXT},
    )
    assert update.status_code == 200
    assert update.json()["raw_text"] == UPDATED_TEXT
    # Henüz reanalyze çağrılmadı - eski required_skills hâlâ duruyor
    assert update.json()["required_skills"] == ["Python", "FastAPI"]

    # 4) Yeniden Analiz Et — eski skor kalır, outdated uyarısı gelir
    reanalyze = await client.post(f"/api/listings/{listing_id}/reanalyze", headers=headers)
    assert reanalyze.status_code == 200
    detail = reanalyze.json()
    assert detail["required_skills"] == ["Python", "FastAPI", "Kubernetes"]
    assert detail["nice_to_have"] == ["Docker", "AWS"]
    assert detail["seniority"] == "mid"
    assert detail["score"] == 60.0
    assert detail["match_outdated"] is True

    match_row = (
        await test_session.execute(select(Match).where(Match.listing_id == listing_id))
    ).scalar_one_or_none()
    assert match_row is not None
    assert match_row.score == 60.0

    # 5) Eşleşmeyi Güncelle — skor yenilenir, outdated kalkar
    rematch = await client.post(f"/api/listings/{listing_id}/rematch", headers=headers)
    assert rematch.status_code == 200
    rematch_detail = rematch.json()
    assert rematch_detail["score"] == 85.0
    assert rematch_detail["matched_skills"] == ["Python", "FastAPI", "Kubernetes"]
    assert rematch_detail["match_outdated"] is False

    listing_row = (
        await test_session.execute(select(JobListing).where(JobListing.id == listing_id))
    ).scalar_one()
    assert listing_row.seniority == "mid"


@pytest.mark.asyncio
async def test_reanalyze_unknown_listing_returns_404(client: AsyncClient):
    headers = await _register_and_login(client)
    response = await client.post("/api/listings/does-not-exist/reanalyze", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rematch_unknown_listing_returns_404(client: AsyncClient):
    headers = await _register_and_login(client)
    response = await client.post("/api/listings/does-not-exist/rematch", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_reanalyze_rejects_other_users_listing(client: AsyncClient, test_session):
    """Sahiplik kontrolü: başka kullanıcının ilanını reanalyze edemezsin"""
    owner_headers = await _register_and_login(client)
    analyze = await client.post(
        "/api/analyze",
        headers=owner_headers,
        json={"listing_text": INITIAL_TEXT},
    )
    listing_id = analyze.json()["listing_id"]

    other_headers = await _register_and_login(client)
    response = await client.post(f"/api/listings/{listing_id}/reanalyze", headers=other_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_reanalyze_and_rematch_require_authentication(client: AsyncClient):
    for path in ("reanalyze", "rematch"):
        response = await client.post(f"/api/listings/some-id/{path}")
        assert response.status_code == 403
