"""Redis tabanlı basit rate limit (auth + AI endpoint'leri)."""

from app.config import settings
from app.logging_config import get_logger
from fastapi import HTTPException, Request, status

logger = get_logger("rate_limit")


async def _increment(key: str, window_seconds: int) -> int:
    from app.redis_client import get_redis

    redis = get_redis()
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, window_seconds)
    return int(count)


def client_key(request: Request, suffix: str) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    ip = (forwarded.split(",")[0].strip() if forwarded else None) or (
        request.client.host if request.client else "unknown"
    )
    return f"rl:{suffix}:{ip}"


async def enforce_rate_limit(
    request: Request,
    *,
    suffix: str,
    limit: int,
    window_seconds: int = 60,
) -> None:
    """Aşımda 429. Redis yoksa / test ortamında fail-open."""
    if settings.ENVIRONMENT == "test":
        return
    try:
        count = await _increment(client_key(request, suffix), window_seconds)
    except Exception as exc:  # noqa: BLE001
        logger.warning("rate_limit_unavailable", error=str(exc))
        return
    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Çok fazla istek. Lütfen kısa süre sonra tekrar deneyin.",
        )
