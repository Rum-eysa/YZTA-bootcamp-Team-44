"""Analiz Ajanı testleri (mock Gemini - gerçek API çağrısı yapılmaz)"""
from unittest.mock import AsyncMock

import pytest

from app.agents.listing_analysis import AnalyzeListingAgent
from app.exceptions import GeminiAPIException, ValidationException


class FakeGeminiClient:
    """generate_with_tools çağrısını simüle eder: verilen tool fonksiyonunu
    sahte argümanlarla çağırır, gerçek GeminiClient'a hiç dokunmaz."""

    def __init__(self, fake_args: dict | None):
        self.fake_args = fake_args
        self.generate_with_tools = AsyncMock(side_effect=self._call_tool)

    async def _call_tool(self, prompt: str, tools: list):
        if self.fake_args is not None:
            tools[0](**self.fake_args)
        return "ok"


@pytest.mark.asyncio
async def test_analyze_extracts_structured_data():
    """Normal bir ilan metni doğru şekilde JSON'a çevrilmeli"""
    fake_args = {
        "required_skills": ["Python", "FastAPI"],
        "nice_to_have_skills": ["Docker"],
        "seniority": "mid",
        "position_title": "Backend Developer",
        "confidence": 0.95,
    }
    agent = AnalyzeListingAgent(client=FakeGeminiClient(fake_args))

    result = await agent.analyze(
        "Python ve FastAPI bilen mid-level backend developer ariyoruz."
    )

    assert result["required_skills"] == ["Python", "FastAPI"]
    assert result["nice_to_have_skills"] == ["Docker"]
    assert result["seniority"] == "mid"
    assert result["position_title"] == "Backend Developer"
    assert result["confidence"] == 0.95


@pytest.mark.asyncio
async def test_analyze_empty_listing_raises_validation_error():
    """Boş/whitespace-only girdi Gemini'ye hiç gitmeden reddedilmeli"""
    agent = AnalyzeListingAgent(client=FakeGeminiClient(None))

    with pytest.raises(ValidationException):
        await agent.analyze("   ")


@pytest.mark.asyncio
async def test_analyze_messy_listing_returns_low_confidence():
    """Eksik/dağınık ilan metinlerinde ajan çökmemeli, düşük confidence ile devam etmeli"""
    fake_args = {
        "required_skills": ["belirsiz"],
        "nice_to_have_skills": [],
        "seniority": "unknown",
        "position_title": "belirsiz",
        "confidence": 0.3,
    }
    agent = AnalyzeListingAgent(client=FakeGeminiClient(fake_args))

    result = await agent.analyze("acil eleman ariyoz maas iyi")

    assert result["confidence"] == 0.3
    assert result["seniority"] == "unknown"


@pytest.mark.asyncio
async def test_analyze_raises_when_gemini_never_calls_tool():
    """Gemini function calling'i hiç tetiklemezse (ör. API hatası/anlayamadıysa)
    sessizce boş dönmek yerine anlaşılır bir hata fırlatılmalı"""
    agent = AnalyzeListingAgent(client=FakeGeminiClient(None))

    with pytest.raises(GeminiAPIException):
        await agent.analyze("bu bir ilan metni")
