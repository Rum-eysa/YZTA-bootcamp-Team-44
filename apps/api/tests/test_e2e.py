"""US-031: Uçtan uca backend akış testi (mock Gemini/Tectonic, gerçek HTTP + JWT + DB)

Zincir: register -> login -> profile -> analyze -> match -> generate-cv
-> generate-cover-letter. Route testlerinden farkı: kimlik doğrulama
dependency_overrides ile değil, gerçek JWT token'ıyla yapılır - böylece
auth middleware'i, route'lar ve DB kalıcılığı tek akışta doğrulanır.
"""
import json
import uuid

import pytest
import pytest_asyncio
from app.agents.cover_letter import get_cover_letter_agent
from app.agents.cv_generation import get_cv_generation_agent
from app.agents.listing_analysis import get_listing_analysis_agent
from app.agents.matching import get_matching_agent
from app.main import app
from app.models import Document, JobListing, Match, User
from httpx import AsyncClient

LISTING_TEXT = (
    "Acme Yazılım A.Ş. Backend Developer (Junior) arıyor. Python, FastAPI ve "
    "PostgreSQL zorunlu; Docker ve Redis artı. İstanbul, hibrit çalışma."
)

ANALYSIS = {
    "position_title": "Backend Developer",
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "nice_to_have_skills": ["Docker", "Redis"],
    "seniority": "junior",
    "confidence": 0.92,
}


class StubAnalysisAgent:
    async def analyze(self, listing_text: str):
        return dict(ANALYSIS)


class StubMatchingAgent:
    async def match_and_save(self, db, user_id, listing_id, user_profile, job_analysis):
        match = Match(
            user_id=user_id,
            listing_id=listing_id,
            score=71.4,
            matched_skills=json.dumps(["python", "fastapi"]),
            missing_skills=json.dumps(["postgresql"]),
        )
        db.add(match)
        await db.commit()
        await db.refresh(match)
        return match


class StubCoverLetterAgent:
    async def generate_and_save(self, db, user_id, listing_id, **kwargs):
        company = kwargs.get("company_name") or "belirtilen şirket"
        doc = Document(
            user_id=user_id,
            listing_id=listing_id,
            doc_type="cover_letter",
            cover_letter_text=f"Sayın {company} ekibi, başvurumu sunarım...",
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc


class StubCVAgent:
    async def generate_and_save(self, db, user_id, listing_id, **kwargs):
        doc = Document(
            user_id=user_id,
            listing_id=listing_id,
            doc_type="cv",
            cv_url=f"http://localhost:9000/cv-documents/cv/{user_id}/e2e-test.pdf",
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc


@pytest.fixture(autouse=True)
def _stub_agents():
    """Tüm ajanları mock'lar - test sırasında gerçek Gemini/Tectonic çağrısı yok"""
    app.dependency_overrides[get_listing_analysis_agent] = lambda: StubAnalysisAgent()
    app.dependency_overrides[get_matching_agent] = lambda: StubMatchingAgent()
    app.dependency_overrides[get_cover_letter_agent] = lambda: StubCoverLetterAgent()
    app.dependency_overrides[get_cv_generation_agent] = lambda: StubCVAgent()
    yield
    for dep in (
        get_listing_analysis_agent,
        get_matching_agent,
        get_cover_letter_agent,
        get_cv_generation_agent,
    ):
        app.dependency_overrides.pop(dep, None)


@pytest_asyncio.fixture
async def seeded_listing(test_session) -> str:
    """Test fixture: önceden analiz edilmiş bir ilan (seed listing)"""
    listing = JobListing(
        title="Backend Developer",
        company="Acme Yazılım A.Ş.",
        raw_text=LISTING_TEXT,
        parsed_json=json.dumps(ANALYSIS, ensure_ascii=False),
        analysis_status="completed",
    )
    test_session.add(listing)
    await test_session.commit()
    await test_session.refresh(listing)
    return listing.id


async def _register_and_login(client: AsyncClient) -> tuple[str, dict]:
    """Gerçek auth akışı: register + login, (email, auth_headers) döner"""
    email = f"e2e-{uuid.uuid4()}@example.com"
    register = await client.post(
        "/api/auth/register",
        json={"email": email, "password": "E2eTestPass123", "full_name": "E2E Kullanıcı"},
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/auth/login", json={"email": email, "password": "E2eTestPass123"}
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return email, {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_full_application_flow(client: AsyncClient):
    """login -> profile -> analyze -> match -> generate-cv -> generate-cover-letter"""
    _, headers = await _register_and_login(client)

    # 1) Profil doldur
    profile = await client.patch(
        "/api/profiles/me",
        headers=headers,
        json={
            "target_position": "Backend Developer",
            "seniority": "junior",
            "experience_years": 1,
            "skills": ["Python", "FastAPI", "Git"],
            "experience_summary": "Staj sırasında FastAPI ile REST API geliştirdi.",
            "tone_preference": "professional",
        },
    )
    assert profile.status_code == 200
    assert profile.json()["skills"] == ["Python", "FastAPI", "Git"]

    # 2) İlan analizi
    analyze = await client.post(
        "/api/analyze",
        headers=headers,
        json={"listing_text": LISTING_TEXT, "company_name": "Acme Yazılım A.Ş."},
    )
    assert analyze.status_code == 200
    listing_id = analyze.json()["listing_id"]
    assert analyze.json()["required_skills"] == ANALYSIS["required_skills"]

    # 3) Eşleştirme
    match = await client.post("/api/match", headers=headers, json={"listing_id": listing_id})
    assert match.status_code == 200
    assert match.json()["score"] == 71.4
    assert match.json()["cached"] is False

    # 4) CV üretimi
    cv = await client.post("/api/generate-cv", headers=headers, json={"listing_id": listing_id})
    assert cv.status_code == 200
    assert cv.json()["cv_url"].endswith(".pdf")

    # 5) Önyazı üretimi - şirket adı ilan kaydından akmalı
    letter = await client.post(
        "/api/generate-cover-letter", headers=headers, json={"listing_id": listing_id}
    )
    assert letter.status_code == 200
    assert letter.json()["company_name"] == "Acme Yazılım A.Ş."
    assert "Acme Yazılım A.Ş." in letter.json()["cover_letter_text"]


@pytest.mark.asyncio
async def test_flow_with_seeded_listing_and_match_cache(client: AsyncClient, seeded_listing: str):
    """Seed ilan üzerinden akış + ikinci match çağrısının cache'den dönmesi"""
    _, headers = await _register_and_login(client)

    first = await client.post("/api/match", headers=headers, json={"listing_id": seeded_listing})
    assert first.status_code == 200
    assert first.json()["cached"] is False

    second = await client.post("/api/match", headers=headers, json={"listing_id": seeded_listing})
    assert second.status_code == 200
    assert second.json()["cached"] is True
    assert second.json()["score"] == first.json()["score"]


@pytest.mark.asyncio
async def test_invalid_listing_id_returns_404_on_every_step(client: AsyncClient):
    """Hata senaryosu: geçersiz listing_id -> zincirin her adımı 404 dönmeli"""
    _, headers = await _register_and_login(client)

    for path in ("/api/match", "/api/generate-cv", "/api/generate-cover-letter"):
        response = await client.post(
            path, headers=headers, json={"listing_id": "gecersiz-listing-id"}
        )
        assert response.status_code == 404, f"{path} 404 dönmedi"


@pytest.mark.asyncio
async def test_chain_rejects_requests_without_token(client: AsyncClient):
    """Korumalı adımlar token'sız 403 dönmeli - auth zinciri gerçekten devrede"""
    for path in ("/api/match", "/api/generate-cv", "/api/generate-cover-letter"):
        response = await client.post(path, json={"listing_id": "x"})
        assert response.status_code == 403, f"{path} auth istemedi"


@pytest.mark.asyncio
async def test_full_journey_persists_all_records(client: AsyncClient, test_session):
    """US-034: her adımın DB kalıcılığı - listing, match ve 2 document kaydı

    HTTP zinciri US-031'deki ile aynı; bu test her adımdan sonra gerçek test
    veritabanında beklenen satırın oluştuğunu ayrıca doğrular.
    """
    from sqlalchemy import select

    email, headers = await _register_and_login(client)

    # register -> users tablosunda kayıt var
    user_row = (await test_session.execute(select(User).where(User.email == email))).scalar_one()
    assert user_row.is_active

    # profile update -> alanlar DB'ye yazıldı (JSON string olarak)
    await client.patch(
        "/api/profiles/me",
        headers=headers,
        json={"skills": ["Python", "FastAPI"], "seniority": "junior"},
    )
    await test_session.refresh(user_row)
    assert json.loads(user_row.skills) == ["Python", "FastAPI"]
    assert user_row.seniority == "junior"

    # analyze -> job_listings satırı: şirket, parsed_json, status, sahiplik
    analyze = await client.post(
        "/api/analyze",
        headers=headers,
        json={"listing_text": LISTING_TEXT, "company_name": "Acme Yazılım A.Ş."},
    )
    listing_id = analyze.json()["listing_id"]
    listing_row = (
        await test_session.execute(select(JobListing).where(JobListing.id == listing_id))
    ).scalar_one()
    assert listing_row.company == "Acme Yazılım A.Ş."
    assert listing_row.analysis_status == "completed"
    assert json.loads(listing_row.parsed_json)["position_title"] == "Backend Developer"
    assert listing_row.created_by == user_row.id

    # match -> matches satırı: skor + beceri listeleri
    await client.post("/api/match", headers=headers, json={"listing_id": listing_id})
    match_row = (
        await test_session.execute(
            select(Match).where(Match.user_id == user_row.id, Match.listing_id == listing_id)
        )
    ).scalar_one()
    assert match_row.score == 71.4
    assert json.loads(match_row.matched_skills) == ["python", "fastapi"]
    assert json.loads(match_row.missing_skills) == ["postgresql"]

    # cv + cover letter -> documents'ta tam 2 kayıt, tipleri doğru
    await client.post("/api/generate-cv", headers=headers, json={"listing_id": listing_id})
    await client.post(
        "/api/generate-cover-letter", headers=headers, json={"listing_id": listing_id}
    )
    documents = (
        (
            await test_session.execute(
                select(Document).where(
                    Document.user_id == user_row.id, Document.listing_id == listing_id
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(documents) == 2
    by_type = {d.doc_type: d for d in documents}
    assert set(by_type) == {"cv", "cover_letter"}
    assert by_type["cv"].cv_url.endswith(".pdf")
    assert by_type["cv"].cover_letter_text is None
    assert "Acme Yazılım A.Ş." in by_type["cover_letter"].cover_letter_text
    assert by_type["cover_letter"].cv_url is None
