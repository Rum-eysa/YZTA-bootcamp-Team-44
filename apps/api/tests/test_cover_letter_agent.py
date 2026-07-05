"""Önyazı Ajanı testleri - ton tutarlılığı ve düz metin çıktısı (mock Gemini)"""
from unittest.mock import AsyncMock

import pytest

from app.agents.cover_letter import CoverLetterAgent
from app.exceptions import ValidationException

USER_PROFILE = {"full_name": "Ayşe Yılmaz", "skills": ["Python", "SQL"]}
JOB_ANALYSIS = {"position_title": "Backend Intern", "required_skills": ["Python"]}
MATCHING_GAPS = {"missing_skills": ["Docker"]}


class FakeGeminiClient:
    """generate_text çağrısını simüle eder, gönderilen prompt'u ve sahte metni yakalar"""

    def __init__(self, fake_text: str):
        self.fake_text = fake_text
        self.last_prompt: str | None = None
        self.generate_text = AsyncMock(side_effect=self._generate)

    async def _generate(self, prompt: str, temperature: float = 0.7):
        self.last_prompt = prompt
        return self.fake_text


def _words(n: int) -> str:
    return " ".join(["kelime"] * n)


@pytest.mark.asyncio
async def test_tone_professional_reaches_prompt():
    client = FakeGeminiClient(_words(350))
    agent = CoverLetterAgent(client=client)

    await agent.generate(
        USER_PROFILE, JOB_ANALYSIS, MATCHING_GAPS, tone_preference="professional"
    )

    assert "profesyonel" in client.last_prompt


@pytest.mark.asyncio
async def test_tone_casual_reaches_prompt():
    client = FakeGeminiClient(_words(350))
    agent = CoverLetterAgent(client=client)

    await agent.generate(
        USER_PROFILE, JOB_ANALYSIS, MATCHING_GAPS, tone_preference="casual"
    )

    assert "gündelik" in client.last_prompt


@pytest.mark.asyncio
async def test_tone_confident_reaches_prompt():
    client = FakeGeminiClient(_words(350))
    agent = CoverLetterAgent(client=client)

    await agent.generate(
        USER_PROFILE, JOB_ANALYSIS, MATCHING_GAPS, tone_preference="confident"
    )

    assert "kendinden emin" in client.last_prompt


@pytest.mark.asyncio
async def test_unknown_tone_falls_back_to_professional():
    client = FakeGeminiClient(_words(350))
    agent = CoverLetterAgent(client=client)

    await agent.generate(
        USER_PROFILE, JOB_ANALYSIS, MATCHING_GAPS, tone_preference="bilinmeyen-ton"
    )

    assert "profesyonel" in client.last_prompt


@pytest.mark.asyncio
async def test_markdown_artifacts_are_stripped():
    client = FakeGeminiClient(
        "**Merhaba**, ben #Ayşe. `Python` biliyorum. " + _words(340)
    )
    agent = CoverLetterAgent(client=client)

    result = await agent.generate(USER_PROFILE, JOB_ANALYSIS, MATCHING_GAPS)

    assert "*" not in result
    assert "#" not in result
    assert "`" not in result


@pytest.mark.asyncio
async def test_missing_profile_raises_validation_error():
    client = FakeGeminiClient(_words(350))
    agent = CoverLetterAgent(client=client)

    with pytest.raises(ValidationException):
        await agent.generate({}, JOB_ANALYSIS, MATCHING_GAPS)
