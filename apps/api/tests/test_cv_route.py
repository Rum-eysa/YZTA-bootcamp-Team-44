"""POST /api/generate-cv endpoint testleri (mock CV Ajanı, gerçek Tectonic derlemesi yok)"""
import json
import uuid

import pytest
from app.agents.cv_generation import CVGenerationException, get_cv_generation_agent
from app.dependencies import get_current_user_id
from app.main import app
from app.models import Document, JobListing, User
from httpx import AsyncClient


class _StubCVAgent:
    def __init__(self):
        self.last_extra_prompt = None
        self.last_matching_gaps = None

    async def generate_and_save(
        self,
        db,
        user_id,
        listing_id,
        user_profile,
        job_analysis,
        matching_gaps=None,
        extra_prompt=None,
    ):
        self.last_extra_prompt = extra_prompt
        self.last_matching_gaps = matching_gaps
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


class _StubCVAgentLatexFailure:
    """US-042: Tectonic/LaTeX derlemesi başarısız - agent'ın kendi temiz 422 hatası"""

    async def generate_and_save(
        self,
        db,
        user_id,
        listing_id,
        user_profile,
        job_analysis,
        matching_gaps=None,
        extra_prompt=None,
    ):
        raise CVGenerationException("CV PDF oluşturulamadı: LaTeX derlemesi başarısız oldu.")


class _StubCVAgentServiceUnavailable:
    """US-042: beklenmeyen alt sistem hatası (ör. MinIO'ya erişilemiyor)"""

    async def generate_and_save(
        self,
        db,
        user_id,
        listing_id,
        user_profile,
        job_analysis,
        matching_gaps=None,
        extra_prompt=None,
    ):
        raise ConnectionError("connection refused")


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.pop(get_cv_generation_agent, None)
    app.dependency_overrides.pop(get_current_user_id, None)


async def _seed_user_and_listing(test_session, user_id):
    user = User(id=user_id, email=f"cv-{user_id}@example.com", hashed_password="x")
    listing = JobListing(
        created_by=user_id,
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps({"position_title": "Backend Developer"}),
        analysis_status="completed",
    )
    test_session.add(user)
    await test_session.commit()
    test_session.add(listing)
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


@pytest.mark.asyncio
async def test_generate_cv_latex_failure_returns_422_with_clean_message(
    client: AsyncClient, test_session
):
    """US-042: Tectonic/LaTeX derlemesi başarısız -> 422 + kullanıcı dostu mesaj, stack trace yok"""
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_cv_generation_agent] = lambda: _StubCVAgentLatexFailure()

    response = await client.post("/api/generate-cv", json={"listing_id": listing.id})

    assert response.status_code == 422
    body = response.json()
    assert "LaTeX derlemesi başarısız" in body["detail"]
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


@pytest.mark.asyncio
async def test_generate_cv_service_unavailable_returns_503(client: AsyncClient, test_session):
    """US-042: beklenmeyen alt sistem hatası (ör. MinIO erişilemez) -> 503, stack trace yok"""
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_cv_generation_agent] = lambda: _StubCVAgentServiceUnavailable()

    response = await client.post("/api/generate-cv", json={"listing_id": listing.id})

    assert response.status_code == 503
    body = response.json()
    assert "şu anda kullanılamıyor" in body["detail"]
    assert "Traceback" not in response.text
    assert "connection refused" not in response.text


@pytest.mark.asyncio
async def test_generate_cv_passes_extra_prompt_to_agent(client: AsyncClient, test_session):
    """US-050: extra_prompt gönderildiğinde agent'a iletilmeli"""
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    stub_agent = _StubCVAgent()
    app.dependency_overrides[get_cv_generation_agent] = lambda: stub_agent

    await client.post(
        "/api/generate-cv",
        json={"listing_id": listing.id, "extra_prompt": "Staj motivasyonumu öne çıkar"},
    )

    assert stub_agent.last_extra_prompt == "Staj motivasyonumu öne çıkar"


@pytest.mark.asyncio
async def test_generate_cv_without_extra_prompt_passes_none(client: AsyncClient, test_session):
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    stub_agent = _StubCVAgent()
    app.dependency_overrides[get_cv_generation_agent] = lambda: stub_agent

    await client.post("/api/generate-cv", json={"listing_id": listing.id})

    assert stub_agent.last_extra_prompt is None


@pytest.mark.asyncio
async def test_generate_cv_rejects_too_long_extra_prompt(client: AsyncClient, test_session):
    user_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, user_id)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_cv_generation_agent] = lambda: _StubCVAgent()

    response = await client.post(
        "/api/generate-cv", json={"listing_id": listing.id, "extra_prompt": "a" * 501}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_cv_rejects_other_users_listing(client: AsyncClient, test_session):
    """Sahiplik: başka kullanıcının ilanına karşı CV üretilemez (US-040 genellemesi)"""
    owner_id = str(uuid.uuid4())
    listing = await _seed_user_and_listing(test_session, owner_id)

    attacker_id = str(uuid.uuid4())
    attacker = User(
        id=attacker_id, email=f"cv-attacker-{attacker_id}@example.com", hashed_password="x"
    )
    test_session.add(attacker)
    await test_session.commit()

    app.dependency_overrides[get_current_user_id] = lambda: attacker_id
    app.dependency_overrides[get_cv_generation_agent] = lambda: _StubCVAgent()

    response = await client.post("/api/generate-cv", json={"listing_id": listing.id})

    assert response.status_code == 404
