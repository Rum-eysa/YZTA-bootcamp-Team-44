"""POST /api/analyze endpoint testleri (mock Analiz Ajanı, gerçek Gemini çağrısı yok)"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.agents.listing_analysis import get_listing_analysis_agent
from app.dependencies import get_current_user_id
from app.exceptions import GeminiAPIException
from app.main import app
from app.models import JobListing, User

LISTING_TEXT = (
    "Python ve SQL bilen backend stajyeri arıyoruz. Takım çalışmasına yatkın, "
    "öğrenmeye açık adaylar tercih edilir."
)


class _StubAgent:
    def __init__(self, result=None, error: Exception | None = None):
        self.result = result
        self.error = error

    async def analyze(self, listing_text: str):
        if self.error:
            raise self.error
        return self.result


async def _seed_user_and_auth(test_session) -> str:
    """Test kullanıcısı oluşturur ve get_current_user_id override eder, user_id döner."""
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email=f"analyze-{user_id}@example.com", hashed_password="x")
    test_session.add(user)
    await test_session.commit()
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    return user_id


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.pop(get_listing_analysis_agent, None)
    app.dependency_overrides.pop(get_current_user_id, None)


@pytest.mark.asyncio
async def test_analyze_happy_path(client: AsyncClient, test_session):
    await _seed_user_and_auth(test_session)
    fake_result = {
        "required_skills": ["Python", "SQL"],
        "nice_to_have_skills": ["Docker"],
        "seniority": "junior",
        "position_title": "Backend Intern",
        "confidence": 0.9,
    }
    app.dependency_overrides[get_listing_analysis_agent] = lambda: _StubAgent(
        result=fake_result
    )

    response = await client.post(
        "/api/analyze", json={"listing_text": LISTING_TEXT}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["required_skills"] == ["Python", "SQL"]
    assert data["nice_to_have"] == ["Docker"]
    assert data["seniority"] == "junior"
    assert data["position_title"] == "Backend Intern"
    assert data["confidence"] == 0.9
    assert "listing_id" in data and data["listing_id"]


@pytest.mark.asyncio
async def test_analyze_saves_to_job_listings(client: AsyncClient, test_session):
    user_id = await _seed_user_and_auth(test_session)
    fake_result = {
        "required_skills": ["Python"],
        "nice_to_have_skills": [],
        "seniority": "mid",
        "position_title": "Dev",
        "confidence": 0.8,
    }
    app.dependency_overrides[get_listing_analysis_agent] = lambda: _StubAgent(
        result=fake_result
    )

    response = await client.post(
        "/api/analyze",
        json={"listing_text": LISTING_TEXT, "company_name": "Acme", "location": "İstanbul"},
    )
    listing_id = response.json()["listing_id"]

    result = await test_session.execute(
        select(JobListing).where(JobListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()

    assert listing is not None
    assert listing.raw_text == LISTING_TEXT
    assert listing.analysis_status == "completed"
    assert listing.title == "Dev"
    assert listing.created_by == user_id
    assert listing.company == "Acme"
    assert listing.location == "İstanbul"
    assert listing.application_stage == "review"


@pytest.mark.asyncio
async def test_analyze_short_listing_text_returns_422(client: AsyncClient):
    app.dependency_overrides[get_current_user_id] = lambda: "u"
    response = await client.post("/api/analyze", json={"listing_text": "kisa metin"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_empty_listing_text_returns_422(client: AsyncClient):
    app.dependency_overrides[get_current_user_id] = lambda: "u"
    response = await client.post("/api/analyze", json={"listing_text": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_missing_field_returns_422(client: AsyncClient):
    app.dependency_overrides[get_current_user_id] = lambda: "u"
    response = await client.post("/api/analyze", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_requires_authentication(client: AsyncClient):
    response = await client.post("/api/analyze", json={"listing_text": LISTING_TEXT})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_analyze_agent_error_returns_503(client: AsyncClient):
    app.dependency_overrides[get_current_user_id] = lambda: "u"
    app.dependency_overrides[get_listing_analysis_agent] = lambda: _StubAgent(
        error=GeminiAPIException("Gemini failed")
    )

    response = await client.post(
        "/api/analyze", json={"listing_text": LISTING_TEXT}
    )

    assert response.status_code == 503
    assert response.json()["error_code"] == "GEMINI_API_ERROR"
