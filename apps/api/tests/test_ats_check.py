"""ATS check endpoint ve ajan yardımcıları testleri."""
from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest
from app.agents.ats_check import (
    AtsCheckAgent,
    collect_heuristics,
    get_ats_check_agent,
    normalize_ats_result,
    score_to_rating,
)
from app.exceptions import ValidationException
from app.main import app
from httpx import AsyncClient
from pypdf import PdfWriter


def _make_pdf_bytes(text: str = "John Doe\nemail@example.com\nExperience\nSkills Python") -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    # pypdf blank page has no text layer; agent tests mock extract or use heuristics unit tests.
    # For route tests we mock the agent entirely.
    buf = BytesIO()
    writer.write(buf)
    data = buf.getvalue()
    # Ensure magic header
    assert data.startswith(b"%PDF")
    return data


@pytest.fixture(autouse=True)
def _clear_ats_override():
    yield
    app.dependency_overrides.pop(get_ats_check_agent, None)


def test_score_to_rating_bands():
    assert score_to_rating(95) == "mukemmel"
    assert score_to_rating(80) == "iyi"
    assert score_to_rating(60) == "orta"
    assert score_to_rating(40) == "iyilestirilebilir"
    assert score_to_rating(10) == "iyilestirilmeli"


def test_normalize_ats_result_averages_and_clamps():
    result = normalize_ats_result(
        {
            "tasarim": {"score": 100, "feedback": "ok"},
            "duzen": {"score": 50, "feedback": "orta"},
            "icerik": {"score": 80, "feedback": "iyi"},
            "summary": "Genel özet",
            "suggestions": ["A", "B", ""],
        }
    )
    assert result["overall_score"] == 77
    assert result["overall_rating"] == "iyi"
    assert result["categories"]["duzen"]["rating"] == "iyilestirilebilir"
    assert result["suggestions"] == ["A", "B"]


def test_normalize_boosts_careertrack_design_layout():
    result = normalize_ats_result(
        {
            "tasarim": {"score": 70, "feedback": "orta tasarım"},
            "duzen": {"score": 60, "feedback": "orta düzen"},
            "icerik": {"score": 80, "feedback": "iyi içerik"},
            "summary": "özet",
            "suggestions": ["Tasarımı sadeleştirin", "İçeriğe metrik ekleyin"],
        },
        careertrack_cv=True,
    )
    assert result["categories"]["tasarim"]["score"] == 100
    assert result["categories"]["duzen"]["score"] == 100
    assert result["categories"]["tasarim"]["rating"] == "mukemmel"
    assert result["categories"]["duzen"]["rating"] == "mukemmel"
    assert result["categories"]["icerik"]["score"] == 80
    assert result["overall_score"] == 93
    assert "İçeriğe metrik ekleyin" in result["suggestions"]
    assert not any("Tasarım" in s or "tasarım" in s.lower() for s in result["suggestions"])


def test_collect_heuristics_detects_contact_and_sections():
    text = (
        "Ada Lovelace\nada@example.com\n+90 532 000 00 00\n"
        "Experience\nSoftware Engineer\nEducation\nSkills\nPython, FastAPI"
    )
    h = collect_heuristics(text, page_count=1)
    assert h["has_email"] is True
    assert h["has_phone"] is True
    assert "experience" in h["detected_sections"]
    assert "education" in h["detected_sections"]
    assert "skills" in h["detected_sections"]


@pytest.mark.asyncio
async def test_agent_rejects_non_pdf_bytes():
    agent = AtsCheckAgent(client=AsyncMock())
    with pytest.raises(ValidationException):
        await agent.analyze(b"not-a-pdf")


@pytest.mark.asyncio
async def test_ats_check_rejects_non_pdf(client: AsyncClient):
    response = await client.post(
        "/api/ats-check",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_ats_check_rejects_empty(client: AsyncClient):
    response = await client.post(
        "/api/ats-check",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_ats_check_happy_path(client: AsyncClient):
    fake_agent = AsyncMock()
    fake_agent.analyze = AsyncMock(
        return_value={
            "overall_score": 88,
            "overall_rating": "iyi",
            "categories": {
                "tasarim": {"score": 90, "rating": "mukemmel", "feedback": "Temiz"},
                "duzen": {"score": 85, "rating": "iyi", "feedback": "İyi sıra"},
                "icerik": {"score": 89, "rating": "iyi", "feedback": "Zengin"},
            },
            "summary": "ATS uyumu iyi",
            "suggestions": ["Tek sütun kullanın"],
        }
    )
    app.dependency_overrides[get_ats_check_agent] = lambda: fake_agent

    with patch(
        "app.routes.ats_check.extract_pdf_text",
        return_value=("Sample CV text with enough content for ATS.", 1),
    ):
        response = await client.post(
            "/api/ats-check",
            files={"file": ("cv.pdf", _make_pdf_bytes(), "application/pdf")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["overall_score"] == 88
    assert body["overall_rating"] == "iyi"
    assert body["categories"]["tasarim"]["score"] == 90
    fake_agent.analyze.assert_awaited_once()


@pytest.mark.asyncio
async def test_ats_check_daily_limit(client: AsyncClient):
    fake_agent = AsyncMock()
    fake_agent.analyze = AsyncMock(
        return_value={
            "overall_score": 70,
            "overall_rating": "orta",
            "categories": {
                "tasarim": {"score": 70, "rating": "orta", "feedback": ""},
                "duzen": {"score": 70, "rating": "orta", "feedback": ""},
                "icerik": {"score": 70, "rating": "orta", "feedback": ""},
            },
            "summary": "ok",
            "suggestions": [],
        }
    )
    app.dependency_overrides[get_ats_check_agent] = lambda: fake_agent

    # ENVIRONMENT=test normalde rate limit no-op; burada bilerek aktifleştiriyoruz.
    with (
        patch(
            "app.routes.ats_check.extract_pdf_text",
            return_value=("Sample CV text with enough content for ATS.", 1),
        ),
        patch("app.routes.ats_check.enforce_rate_limit") as enforce,
    ):
        # İlk çağrı geçer, ikinci 429
        async def _limit_side_effect(request, *, suffix, limit, window_seconds):
            key = getattr(_limit_side_effect, "count", 0)
            _limit_side_effect.count = key + 1
            if key >= 1:
                from fastapi import HTTPException, status

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Çok fazla istek. Lütfen kısa süre sonra tekrar deneyin.",
                )

        _limit_side_effect.count = 0
        enforce.side_effect = _limit_side_effect

        first = await client.post(
            "/api/ats-check",
            files={"file": ("cv.pdf", _make_pdf_bytes(), "application/pdf")},
        )
        second = await client.post(
            "/api/ats-check",
            files={"file": ("cv.pdf", _make_pdf_bytes(), "application/pdf")},
        )

    assert first.status_code == 200
    assert second.status_code == 429
