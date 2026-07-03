"""Async SQLAlchemy engine ve session yonetimi"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

_async_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Supabase'in transaction pooler'ı (PgBouncer, port 6543) server-side prepared
# statement'ları desteklemez; asyncpg'nin statement cache'ini kapatmak gerekir.
_connect_args = {"statement_cache_size": 0} if ":6543" in _async_url else {}

engine = create_async_engine(
    _async_url, echo=settings.DEBUG, pool_pre_ping=True, connect_args=_connect_args
)

AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
