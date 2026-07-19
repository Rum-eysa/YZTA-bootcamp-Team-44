"""Orkestratör testleri (US-030) + uçtan uca akış (US-031/US-034)

Mock ajanlarla: gerçek Gemini/Tectonic çağrısı yok.
"""
import json
import uuid

import pytest
from app.agents.orchestrator import ApplicationOrchestrator, OrchestrationError, get_orchestrator
from app.dependencies import get_current_user_id
from app.exceptions import GeminiAPIException
from app.main import app
from app.models import Document, JobListing, Match, User
from httpx import AsyncClient

ANALYSIS = {
    "position_title": "Backend Developer",
    "required_skills": ["Python", "FastAPI"],
    "nice_to_have_skills": ["Docker"],
    "seniority": "junior",
    "confidence": 0.9,
}

LISTING_TEXT = (
    "Acme Yazılım Backend Developer arıyor. Python ve FastAPI zorunlu, "
    "Docker artı. Junior seviye, İstanbul hibrit."
)


class StubAnalysisAgent:
    def __init__(self, fail_times: int = 0):
        self.fail_times = fail_times
        self.calls = 0

    async def analyze(self, listing_text: str):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise GeminiAPIException("quota")
        return dict(ANALYSIS)


class StubMatchingAgent:
    async def match_and_save(self, db, user_id, listing_id, user_profile, job_analysis):
        match = Match(
            user_id=user_id,
            listing_id=listing_id,
            score=75.0,
            matched_skills=json.dumps(["python"]),
            missing_skills=json.dumps(["fastapi"]),
        )
        db.add(match)
        await db.commit()
        await db.refresh(match)
        return match


class StubCoverLetterAgent:
    def __init__(self, fail: bool = False):
        self.fail = fail
        self.received_gaps = None

    async def generate_and_save(self, db, user_id, listing_id, **kwargs):
        if self.fail:
            raise GeminiAPIException("quota exceeded")
        self.received_gaps = kwargs.get("matching_gaps")
        doc = Document(
            user_id=user_id,
            listing_id=listing_id,
            doc_type="cover_letter",
            cover_letter_text="Sayın Yetkili...",
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
            cv_url="http://localhost:9000/cv-documents/cv/fake.pdf",
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc


def _orchestrator(**overrides) -> ApplicationOrchestrator:
    return ApplicationOrchestrator(
        analysis_agent=overrides.get("analysis", StubAnalysisAgent()),
        matching_agent=overrides.get("matching", StubMatchingAgent()),
        cover_letter_agent=overrides.get("cover_letter", StubCoverLetterAgent()),
        cv_agent=overrides.get("cv", StubCVAgent()),
    )


async def _seed_user(test_session) -> str:
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"orch-{user_id}@example.com",
        hashed_password="x",
        skills=json.dumps(["Python", "SQL"]),
        seniority="junior",
        tone_preference="professional",
    )
    test_session.add(user)
    await test_session.commit()
    return user_id


@pytest.mark.asyncio
async def test_full_flow_from_listing_text(test_session):
    """E2E: metin -> analiz -> eşleşme -> önyazı -> CV, hepsi tek çağrıda"""
    user_id = await _seed_user(test_session)
    orch = _orchestrator()

    result = await orch.process(
        db=test_session, user_id=user_id, listing_text=LISTING_TEXT, company_name="Acme"
    )

    assert result["listing_id"]
    assert result["analysis"]["position_title"] == "Backend Developer"
    assert result["match"]["score"] == 75.0
    assert result["cover_letter_text"] == "Sayın Yetkili..."
    assert result["cv_url"].endswith(".pdf")
    assert result["errors"] == []
    steps = {s["step"]: s["status"] for s in result["timeline"]}
    assert steps == {
        "analysis": "completed",
        "matching": "completed",
        "cover_letter": "completed",
        "cv": "completed",
    }


@pytest.mark.asyncio
async def test_flow_with_existing_listing_skips_analysis(test_session):
    user_id = await _seed_user(test_session)
    listing = JobListing(
        created_by=user_id,
        title="Backend Developer",
        raw_text=LISTING_TEXT,
        parsed_json=json.dumps(ANALYSIS),
        analysis_status="completed",
    )
    test_session.add(listing)
    await test_session.commit()
    await test_session.refresh(listing)

    orch = _orchestrator()
    result = await orch.process(db=test_session, user_id=user_id, listing_id=listing.id)

    step_names = [s["step"] for s in result["timeline"]]
    assert "analysis" not in step_names
    assert result["listing_id"] == listing.id
    assert result["match"]["score"] == 75.0


@pytest.mark.asyncio
async def test_transient_analysis_error_is_retried(test_session):
    """Gemini 1 kez düşerse retry ile kurtarılmalı"""
    user_id = await _seed_user(test_session)
    flaky = StubAnalysisAgent(fail_times=1)
    orch = _orchestrator(analysis=flaky)

    result = await orch.process(db=test_session, user_id=user_id, listing_text=LISTING_TEXT)

    assert flaky.calls == 2
    analysis_step = next(s for s in result["timeline"] if s["step"] == "analysis")
    assert analysis_step["attempts"] == 2


@pytest.mark.asyncio
async def test_transient_error_backoff_and_gives_up_after_max_attempts(test_session):
    """US-041: kalıcı hata max 2 denemede pes eder, denemeler arası backoff gerçekten bekler"""
    user_id = await _seed_user(test_session)
    always_fails = StubAnalysisAgent(fail_times=99)
    orch = _orchestrator(analysis=always_fails)

    with pytest.raises(OrchestrationError) as exc_info:
        await orch.process(db=test_session, user_id=user_id, listing_text=LISTING_TEXT)

    assert exc_info.value.step == "analysis"
    assert always_fails.calls == 2  # 1 ilk deneme + 1 retry, sonra pes eder - 3. deneme yok


@pytest.mark.asyncio
async def test_retry_waits_with_exponential_backoff(test_session):
    """2. deneme öncesi gerçekten bekleniyor (anında retry değil)"""
    user_id = await _seed_user(test_session)
    flaky = StubAnalysisAgent(fail_times=1)
    orch = _orchestrator(analysis=flaky)

    result = await orch.process(db=test_session, user_id=user_id, listing_text=LISTING_TEXT)

    analysis_step = next(s for s in result["timeline"] if s["step"] == "analysis")
    # _BASE_BACKOFF_SECONDS=0.2s bekleniyor olmalı (biraz tolerans ile)
    assert analysis_step["duration_ms"] >= 180


@pytest.mark.asyncio
async def test_cover_letter_failure_does_not_break_cv(test_session):
    """Önyazı düşse bile CV üretilmeli - kısmi sonuç dayanıklılığı"""
    user_id = await _seed_user(test_session)
    orch = _orchestrator(cover_letter=StubCoverLetterAgent(fail=True))

    result = await orch.process(db=test_session, user_id=user_id, listing_text=LISTING_TEXT)

    assert result["cover_letter_text"] is None
    assert result["cv_url"].endswith(".pdf")
    assert len(result["errors"]) == 1
    assert result["errors"][0].startswith("cover_letter:")
    steps = {s["step"]: s["status"] for s in result["timeline"]}
    assert steps["cover_letter"] == "failed"
    assert steps["cv"] == "completed"


@pytest.mark.asyncio
async def test_second_run_uses_cached_match(test_session):
    """Aynı user+listing için ikinci akış eşleştirmeyi cache'den okumalı"""
    user_id = await _seed_user(test_session)
    orch = _orchestrator()

    first = await orch.process(
        db=test_session, user_id=user_id, listing_text=LISTING_TEXT, generate_cv=False
    )
    second = await orch.process(
        db=test_session,
        user_id=user_id,
        listing_id=first["listing_id"],
        generate_cv=False,
        generate_cover_letter=False,
    )

    match_step = next(s for s in second["timeline"] if s["step"] == "matching")
    assert match_step["status"] == "cached"
    assert second["match"]["score"] == first["match"]["score"]


@pytest.mark.asyncio
async def test_cover_letter_receives_match_gaps(test_session):
    """Hafıza katmanı: eşleştirme çıktısı önyazı ajanına bağlam olarak akmalı"""
    user_id = await _seed_user(test_session)
    cover = StubCoverLetterAgent()
    orch = _orchestrator(cover_letter=cover)

    await orch.process(
        db=test_session, user_id=user_id, listing_text=LISTING_TEXT, generate_cv=False
    )

    assert cover.received_gaps is not None
    assert cover.received_gaps.get("score") == 75.0
    assert "fastapi" in [s.lower() for s in cover.received_gaps.get("missing_skills", [])]


# --- HTTP seviyesi (US-031/US-034 E2E) --------------------------------------


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.pop(get_orchestrator, None)
    app.dependency_overrides.pop(get_current_user_id, None)


@pytest.mark.asyncio
async def test_process_endpoint_full_flow(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_orchestrator] = lambda: _orchestrator()

    response = await client.post(
        "/api/process",
        json={"listing_text": LISTING_TEXT, "company_name": "Acme"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["match"]["score"] == 75.0
    assert data["cover_letter_text"]
    assert data["cv_url"]
    assert data["errors"] == []
    assert len(data["timeline"]) == 4


@pytest.mark.asyncio
async def test_process_endpoint_requires_auth(client: AsyncClient):
    response = await client.post("/api/process", json={"listing_text": LISTING_TEXT})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_process_endpoint_validates_input(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_orchestrator] = lambda: _orchestrator()

    response = await client.post("/api/process", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_process_endpoint_unknown_listing_returns_404(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    app.dependency_overrides[get_orchestrator] = lambda: _orchestrator()

    response = await client.post("/api/process", json={"listing_id": "does-not-exist"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_process_endpoint_rejects_other_users_listing(client: AsyncClient, test_session):
    """Sahiplik: /api/process başkasının listing_id'siyle 404 dönmeli (US-040 genellemesi)"""
    owner_id = await _seed_user(test_session)
    listing = JobListing(
        created_by=owner_id,
        title="Backend Developer",
        raw_text=LISTING_TEXT,
        parsed_json=json.dumps(ANALYSIS),
        analysis_status="completed",
    )
    test_session.add(listing)
    await test_session.commit()
    await test_session.refresh(listing)

    attacker_id = await _seed_user(test_session)
    app.dependency_overrides[get_current_user_id] = lambda: attacker_id
    app.dependency_overrides[get_orchestrator] = lambda: _orchestrator()

    response = await client.post("/api/process", json={"listing_id": listing.id})
    assert response.status_code == 404
