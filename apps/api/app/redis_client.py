"""Async Redis client - token blacklist ve cache için"""
from functools import lru_cache

from app.config import settings
from redis.asyncio import Redis, from_url


@lru_cache
def get_redis() -> Redis:
    return from_url(settings.REDIS_URL, decode_responses=True)
