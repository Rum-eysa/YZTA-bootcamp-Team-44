"""Gözlemlenebilirlik testleri: agent_run telemetrisi + Sentry başlatma davranışı (US-018)"""
from unittest.mock import patch

import pytest
from app import observability
from app.observability import agent_run, capture_exception, init_sentry


@pytest.mark.asyncio
async def test_agent_run_logs_start_and_completion():
    with patch.object(observability, "logger") as mock_logger:
        async with agent_run("demo_agent", extra="x") as run:
            run.set_token_count(42)

    events = [call.args[0] for call in mock_logger.info.call_args_list]
    assert "agent_started" in events
    assert "agent_completed" in events

    completed_kwargs = mock_logger.info.call_args_list[-1].kwargs
    assert completed_kwargs["agent"] == "demo_agent"
    assert completed_kwargs["token_count"] == 42
    assert "duration_ms" in completed_kwargs


@pytest.mark.asyncio
async def test_agent_run_logs_failure_and_reraises():
    with patch.object(observability, "logger") as mock_logger:
        with pytest.raises(ValueError):
            async with agent_run("demo_agent"):
                raise ValueError("boom")

    assert mock_logger.error.called
    error_call = mock_logger.error.call_args
    assert error_call.args[0] == "agent_failed"
    assert error_call.kwargs["agent"] == "demo_agent"
    assert "duration_ms" in error_call.kwargs


def test_init_sentry_noop_in_test_environment():
    # ENVIRONMENT=test olduğu için DSN verilse bile Sentry başlatılmamalı
    with patch.object(observability.settings, "SENTRY_DSN", "https://x@example.com/1"):
        with patch.object(observability.settings, "ENVIRONMENT", "test"):
            assert init_sentry() is False


def test_capture_exception_noop_when_not_initialized():
    # SDK başlatılmadığında hata fırlatmadan sessizce geçmeli
    observability._sentry_initialized = False
    capture_exception(RuntimeError("ignored"))
