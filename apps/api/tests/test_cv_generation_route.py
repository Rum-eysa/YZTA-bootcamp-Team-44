"""POST /api/generate-cv endpoint testleri (mock CV Ajanı, gerçek Tectonic derlemesi yok)"""
import json
import uuid

import pytest
from httpx import AsyncClient

from app.agents.cv_generation import get_cv_generation_agent
from app.dependencies import get_current_user_id
from app.main import app
from app.models import Document, JobListing, User


class _StubCVAgent:
    async def generate_and_save(self, db, user_id, listing_id, user_profile, job_analysis):
        document = Document(
            user_id=user_id,
            listing_id=listing_id,
            doc_type="cv",
            cv_url="http://localhost:9000/cv-documents/cv/fake.pdf",
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.pop(get_cv_generation_agent, None)
    app.dependency_overrides.pop(get_current_user_id, None)


async def _seed_user_and_listing(test_session, user_id):
    user = User(id=user_id, email=f"cv-{user_id}@example.com", hashed_password="x")
    listing = JobListing(
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps({"position_title": "Backend Developer"}),
        analysis_status="completed",
    )
    test_session.add_all([user, listing])
    await test_session.commit()
    await test_session.refresh(listing)
    return listing


@pytest.mark.asyncio
async def test_generate_cv_happy_path(client: AsyncClient, test_session):
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_cv_generation_agent] = lambda: _StubCVAgent()

    response = await client.post("/api/generate-cv", json={"listing_id": listing.id})

    assert response.status_code == 200
    data = response.json()
    assert data["cv_url"] == "http://localhost:9000/cv-documents/cv/fake.pdf"
    assert data["listing_id"] == listing.id


@pytest.mark.asyncio
async def test_generate_cv_unknown_listing_returns_404(client: AsyncClient, test_session):
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email=f"cv2-{user_id}@example.com", hashed_password="x")
    test_session.add(user)
    await test_session.commit()

    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_cv_generation_agent] = lambda: _StubCVAgent()

    response = await client.post("/api/generate-cv", json={"listing_id": "does-not-exist"})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_generate_cv_requires_authentication(client: AsyncClient):
    response = await client.post("/api/generate-cv", json={"listing_id": "some-id"})
    assert response.status_code == 403
