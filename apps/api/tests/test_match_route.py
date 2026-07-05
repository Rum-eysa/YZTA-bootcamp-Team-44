"""POST /api/match endpoint testleri (mock Eşleştirme Ajanı, gerçek Gemini çağrısı yok)"""
import json
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.agents.matching import get_matching_agent
from app.dependencies import get_current_user_id
from app.main import app
from app.models import JobListing, Match, User


class _StubMatchingAgent:
    def __init__(self):
        self.calls = 0

    async def match_and_save(self, db, user_id, listing_id, user_profile, job_analysis):
        self.calls += 1
        match = Match(
            user_id=user_id,
            listing_id=listing_id,
            score=73.7,
            matched_skills=json.dumps(["python", "fastapi"]),
            missing_skills=json.dumps(["postgresql"]),
        )
        db.add(match)
        await db.commit()
        await db.refresh(match)
        return match


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.pop(get_matching_agent, None)
    app.dependency_overrides.pop(get_current_user_id, None)


async def _seed_user_and_listing(test_session, user_id):
    user = User(
        id=user_id,
        email=f"match-{user_id}@example.com",
        hashed_password="x",
        skills=json.dumps(["Python", "FastAPI"]),
        seniority="junior",
    )
    listing = JobListing(
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps(
            {
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "nice_to_have_skills": ["Docker"],
                "seniority": "junior",
            }
        ),
        analysis_status="completed",
    )
    test_session.add_all([user, listing])
    await test_session.commit()
    await test_session.refresh(listing)
    return listing


@pytest.mark.asyncio
async def test_match_happy_path(client: AsyncClient, test_session):
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_matching_agent] = lambda: _StubMatchingAgent()

    response = await client.post("/api/match", json={"listing_id": listing.id})

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 73.7
    assert data["matched_skills"] == ["python", "fastapi"]
    assert data["missing_skills"] == ["postgresql"]
    assert data["cached"] is False


@pytest.mark.asyncio
async def test_match_returns_cached_result_without_calling_agent(
    client: AsyncClient, test_session
):
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    stub_agent = _StubMatchingAgent()
    app.dependency_overrides[get_matching_agent] = lambda: stub_agent

    first = await client.post("/api/match", json={"listing_id": listing.id})
    assert first.json()["cached"] is False
    assert stub_agent.calls == 1

    second = await client.post("/api/match", json={"listing_id": listing.id})
    assert second.status_code == 200
    assert second.json()["cached"] is True
    assert second.json()["score"] == first.json()["score"]
    assert stub_agent.calls == 1  # agent tekrar çağrılmadı


@pytest.mark.asyncio
async def test_match_unknown_listing_returns_404(client: AsyncClient, test_session):
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email=f"match2-{user_id}@example.com", hashed_password="x")
    test_session.add(user)
    await test_session.commit()

    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_matching_agent] = lambda: _StubMatchingAgent()

    response = await client.post("/api/match", json={"listing_id": "does-not-exist"})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_match_requires_authentication(client: AsyncClient):
    response = await client.post("/api/match", json={"listing_id": "some-id"})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_match_saves_to_matches_table(client: AsyncClient, test_session):
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_matching_agent] = lambda: _StubMatchingAgent()

    response = await client.post("/api/match", json={"listing_id": listing.id})
    match_id = response.json()["match_id"]

    result = await test_session.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()

    assert match is not None
    assert match.user_id == user_id
    assert match.listing_id == listing.id
