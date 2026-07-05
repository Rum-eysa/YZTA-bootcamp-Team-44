"""POST /api/generate-cover-letter endpoint testleri (mock Önyazı Ajanı, gerçek Gemini çağrısı yok)"""
import json
import uuid

import pytest
from httpx import AsyncClient

from app.agents.cover_letter import get_cover_letter_agent
from app.dependencies import get_current_user_id
from app.main import app
from app.models import Document, JobListing, User


class _StubCoverLetterAgent:
    def __init__(self):
        self.last_company_name = None

    async def generate_and_save(
        self,
        db,
        user_id,
        listing_id,
        user_profile,
        job_analysis,
        matching_gaps,
        tone_preference="professional",
        company_name=None,
    ):
        self.last_company_name = company_name
        document = Document(
            user_id=user_id,
            listing_id=listing_id,
            doc_type="cover_letter",
            cover_letter_text=f"Sayın {company_name} ekibi, ...",
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.pop(get_cover_letter_agent, None)
    app.dependency_overrides.pop(get_current_user_id, None)


async def _seed_user_and_listing(test_session, user_id, company="Acme Yazılım A.Ş."):
    user = User(id=user_id, email=f"cl-{user_id}@example.com", hashed_password="x")
    listing = JobListing(
        title="Backend Developer",
        company=company,
        raw_text="a" * 60,
        parsed_json=json.dumps({"position_title": "Backend Developer"}),
        analysis_status="completed",
    )
    test_session.add_all([user, listing])
    await test_session.commit()
    await test_session.refresh(listing)
    return listing


@pytest.mark.asyncio
async def test_generate_cover_letter_happy_path(client: AsyncClient, test_session):
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_cover_letter_agent] = lambda: _StubCoverLetterAgent()

    response = await client.post(
        "/api/generate-cover-letter", json={"listing_id": listing.id}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Acme Yazılım A.Ş."
    assert "Acme Yazılım A.Ş." in data["cover_letter_text"]
    assert data["listing_id"] == listing.id


@pytest.mark.asyncio
async def test_generate_cover_letter_passes_company_name_to_agent(
    client: AsyncClient, test_session
):
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id, company="TechNova")
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    stub_agent = _StubCoverLetterAgent()
    app.dependency_overrides[get_cover_letter_agent] = lambda: stub_agent

    await client.post("/api/generate-cover-letter", json={"listing_id": listing.id})

    assert stub_agent.last_company_name == "TechNova"


@pytest.mark.asyncio
async def test_generate_cover_letter_missing_company_falls_back(
    client: AsyncClient, test_session
):
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id, company=None)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_cover_letter_agent] = lambda: _StubCoverLetterAgent()

    response = await client.post(
        "/api/generate-cover-letter", json={"listing_id": listing.id}
    )

    assert response.json()["company_name"] == "belirtilen şirket"


@pytest.mark.asyncio
async def test_generate_cover_letter_unknown_listing_returns_404(
    client: AsyncClient, test_session
):
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email=f"cl2-{user_id}@example.com", hashed_password="x")
    test_session.add(user)
    await test_session.commit()

    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_cover_letter_agent] = lambda: _StubCoverLetterAgent()

    response = await client.post(
        "/api/generate-cover-letter", json={"listing_id": "does-not-exist"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_generate_cover_letter_requires_authentication(client: AsyncClient):
    response = await client.post(
        "/api/generate-cover-letter", json={"listing_id": "some-id"}
    )
    assert response.status_code == 403
