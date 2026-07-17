"""GeminiClient birim testleri: kota, retry, context budget (gerçek Gemini/Redis çağrısı yok)"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.exceptions import GeminiAPIException
from app.services import gemini_client as gemini_client_module
from app.services.gemini_client import (
    FREE_TIER_RPD,
    FREE_TIER_RPM,
    MAX_CONTEXT_TOKENS,
    GeminiClient,
    estimate_tokens,
)
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable


class _FakeRedis:
    """Gerçek Redis yerine bellekte sayaç tutan sahte istemci"""

    def __init__(self):
        self.counters: dict[str, int] = {}
        self.expiries: dict[str, int] = {}

    async def incrby(self, key: str, amount: int) -> int:
        self.counters[key] = self.counters.get(key, 0) + amount
        return self.counters[key]

    async def expire(self, key: str, seconds: int) -> None:
        self.expiries[key] = seconds


@pytest.fixture
def fake_redis():
    return _FakeRedis()


@pytest.fixture
def client(fake_redis, monkeypatch):
    monkeypatch.setattr(gemini_client_module, "get_redis", lambda: fake_redis)
    with patch("app.services.gemini_client.genai.configure"), patch(
        "app.services.gemini_client.genai.GenerativeModel"
    ):
        return GeminiClient(model_name="gemini-test")


# --- Kota testleri (uygulama Redis kotası no-op) ------------------------------


@pytest.mark.asyncio
async def test_quota_is_noop_and_does_not_touch_redis(client, fake_redis):
    for _ in range(FREE_TIER_RPM + 5):
        await client._check_quota()
    await client._check_quota(cost=FREE_TIER_RPD + 1)

    assert fake_redis.counters == {}
    assert fake_redis.expiries == {}


@pytest.mark.asyncio
async def test_quota_never_raises_for_minute_or_daily_overflow(client, fake_redis):
    fake_redis.counters["gemini:quota:minute"] = FREE_TIER_RPM
    fake_redis.counters["gemini:quota:day"] = FREE_TIER_RPD

    await client._check_quota()
    await client._check_quota(cost=2)


# --- Context budget testleri ---------------------------------------------------


def test_estimate_tokens_uses_char_heuristic():
    assert estimate_tokens("a" * 400) == 100


def test_context_budget_allows_prompt_within_limit(client):
    client._check_context_budget("a" * 100)  # raise etmemeli


def test_context_budget_rejects_oversized_prompt(client):
    oversized = "a" * ((MAX_CONTEXT_TOKENS + 1) * 4)
    with pytest.raises(GeminiAPIException, match="too large"):
        client._check_context_budget(oversized)


def test_context_budget_warns_near_limit_without_raising(client, caplog):
    near_limit = "a" * (int(MAX_CONTEXT_TOKENS * 0.85) * 4)
    client._check_context_budget(near_limit)  # raise etmemeli, sadece uyarı loglar


# --- Retry testleri -------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_with_retry_succeeds_first_try(client):
    fake_response = MagicMock(text="ok", usage_metadata=None)
    client.model.generate_content = MagicMock(return_value=fake_response)

    result = await client._generate_with_retry("prompt", generation_config={})

    assert result.text == "ok"
    assert client.model.generate_content.call_count == 1


@pytest.mark.asyncio
async def test_generate_with_retry_recovers_after_transient_errors(client):
    fake_response = MagicMock(text="ok", usage_metadata=None)
    client.model.generate_content = MagicMock(
        side_effect=[
            ServiceUnavailable("temporarily down"),
            ResourceExhausted("quota burst"),
            fake_response,
        ]
    )

    with patch("app.services.gemini_client.asyncio.sleep", new=AsyncMock()):
        result = await client._generate_with_retry("prompt", generation_config={}, max_retries=3)

    assert result.text == "ok"
    assert client.model.generate_content.call_count == 3


@pytest.mark.asyncio
async def test_generate_with_retry_exhausts_and_raises(client):
    client.model.generate_content = MagicMock(side_effect=ServiceUnavailable("still down"))

    with patch("app.services.gemini_client.asyncio.sleep", new=AsyncMock()):
        with pytest.raises(GeminiAPIException, match="unavailable after retries"):
            await client._generate_with_retry("prompt", generation_config={}, max_retries=2)

    assert client.model.generate_content.call_count == 2


@pytest.mark.asyncio
async def test_generate_with_retry_wraps_non_retryable_error(client):
    client.model.generate_content = MagicMock(side_effect=ValueError("boom"))

    with pytest.raises(GeminiAPIException, match="Gemini API call failed"):
        await client._generate_with_retry("prompt", generation_config={})

    assert client.model.generate_content.call_count == 1


@pytest.mark.asyncio
async def test_generate_with_retry_checks_context_budget_before_calling(client):
    client.model.generate_content = MagicMock()
    oversized = "a" * ((MAX_CONTEXT_TOKENS + 1) * 4)

    with pytest.raises(GeminiAPIException, match="too large"):
        await client._generate_with_retry(oversized, generation_config={})

    client.model.generate_content.assert_not_called()


# --- generate_json / generate_text sarmalayıcı testleri -------------------------


@pytest.mark.asyncio
async def test_generate_json_parses_valid_response(client):
    fake_response = MagicMock(text='{"required_skills": ["python"]}', usage_metadata=None)
    client.model.generate_content = MagicMock(return_value=fake_response)

    result = await client.generate_json("prompt", response_schema={})

    assert result == {"required_skills": ["python"]}


@pytest.mark.asyncio
async def test_generate_json_raises_on_malformed_json(client):
    fake_response = MagicMock(text="not json", usage_metadata=None)
    client.model.generate_content = MagicMock(return_value=fake_response)

    with pytest.raises(GeminiAPIException, match="malformed JSON"):
        await client.generate_json("prompt", response_schema={})


@pytest.mark.asyncio
async def test_generate_text_returns_raw_text(client):
    fake_response = MagicMock(text="merhaba", usage_metadata=None)
    client.model.generate_content = MagicMock(return_value=fake_response)

    result = await client.generate_text("prompt")

    assert result == "merhaba"


# --- generate_with_tools testleri ------------------------------------------------


@pytest.mark.asyncio
async def test_generate_with_tools_uses_cost_two_quota_and_returns_text(client, fake_redis):
    fake_chat = MagicMock()
    fake_response = MagicMock(text="function-calling sonucu", usage_metadata=None)
    fake_chat.send_message = MagicMock(return_value=fake_response)
    fake_model = MagicMock()
    fake_model.start_chat = MagicMock(return_value=fake_chat)

    with patch("app.services.gemini_client.genai.GenerativeModel", return_value=fake_model):
        result = await client.generate_with_tools("prompt", tools=[lambda: None])

    assert result == "function-calling sonucu"
    assert fake_redis.counters["gemini:quota:day"] == 2


@pytest.mark.asyncio
async def test_generate_with_tools_wraps_retryable_error(client):
    fake_chat = MagicMock()
    fake_chat.send_message = MagicMock(side_effect=ServiceUnavailable("down"))
    fake_model = MagicMock()
    fake_model.start_chat = MagicMock(return_value=fake_chat)

    with patch("app.services.gemini_client.genai.GenerativeModel", return_value=fake_model):
        with pytest.raises(GeminiAPIException, match="temporarily unavailable"):
            await client.generate_with_tools("prompt", tools=[])


# --- render_prompt / get_gemini_client -------------------------------------------


def test_render_prompt_fills_known_template():
    from app.services.gemini_client import render_prompt

    result = render_prompt("analyze_listing", listing_text="Backend developer aranıyor")
    assert "Backend developer aranıyor" in result


def test_render_prompt_raises_on_unknown_template():
    from app.services.gemini_client import render_prompt

    with pytest.raises(KeyError):
        render_prompt("unknown_template")


def test_get_gemini_client_returns_singleton(monkeypatch):
    monkeypatch.setattr(gemini_client_module, "_client", None)
    with patch("app.services.gemini_client.genai.configure"), patch(
        "app.services.gemini_client.genai.GenerativeModel"
    ):
        first = gemini_client_module.get_gemini_client()
        second = gemini_client_module.get_gemini_client()
    assert first is second
