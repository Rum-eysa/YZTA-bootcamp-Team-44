"""Gözlemlenebilirlik: Sentry hata takibi + ajan telemetrisi (US-018).

Sentry sadece SENTRY_DSN tanımlıysa ve test dışı ortamda başlatılır. `agent_run`
her ajan çalışmasının başlangıç/bitiş, süre (ms) ve token sayısını yapılandırılmış
loglara yazar; request_id log correlation'ı structlog contextvars üzerinden gelir.
"""
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Optional

from app.config import settings
from app.logging_config import get_logger

logger = get_logger("observability")

_sentry_initialized = False


def init_sentry() -> bool:
    """SENTRY_DSN tanımlıysa Sentry SDK'yı başlatır. Test ortamında no-op."""
    global _sentry_initialized
    if _sentry_initialized:
        return True
    if not settings.SENTRY_DSN or settings.ENVIRONMENT == "test":
        return False

    import sentry_sdk
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT or settings.ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[StarletteIntegration()],
        send_default_pii=False,
    )
    _sentry_initialized = True
    logger.info(
        "sentry_initialized",
        environment=settings.SENTRY_ENVIRONMENT or settings.ENVIRONMENT,
    )
    return True


def capture_exception(exc: BaseException) -> None:
    """Yakalanmamış exception'ı Sentry'ye gönderir (SDK başlatılmadıysa no-op)."""
    if not _sentry_initialized:
        return
    import sentry_sdk

    sentry_sdk.capture_exception(exc)


class AgentRun:
    """`agent_run` içinde token sayısını ajanın bildirmesi için hafif taşıyıcı."""

    def __init__(self) -> None:
        self.token_count: Optional[int] = None

    def set_token_count(self, token_count: Optional[int]) -> None:
        self.token_count = token_count


@asynccontextmanager
async def agent_run(agent_name: str, **fields: Any) -> AsyncIterator[AgentRun]:
    """Bir ajan çalışmasını sarmalar; başlangıç/bitiş, süre ve token sayısını loglar."""
    run = AgentRun()
    started_at = time.perf_counter()
    logger.info("agent_started", agent=agent_name, **fields)
    try:
        yield run
    except Exception as exc:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.error(
            "agent_failed",
            agent=agent_name,
            duration_ms=duration_ms,
            error=str(exc),
            **fields,
        )
        raise
    else:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.info(
            "agent_completed",
            agent=agent_name,
            duration_ms=duration_ms,
            token_count=run.token_count,
            **fields,
        )
