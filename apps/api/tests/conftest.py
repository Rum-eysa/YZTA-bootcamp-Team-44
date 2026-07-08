import asyncio
import os

import pytest
import pytest_asyncio
from app.config import settings
from app.database import get_db
from app.main import app
from app.models import Base
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = os.environ.get("TEST_DATABASE_URL") or os.environ.get(
    "DATABASE_URL", settings.DATABASE_URL
)
assert DATABASE_URL is not None, "DATABASE_URL (veya TEST_DATABASE_URL) tanımlı olmalı"
if "TEST_DATABASE_URL" not in os.environ and not DATABASE_URL.rsplit("/", 1)[-1].endswith("_test"):
    base_url, _, db_name = DATABASE_URL.rpartition("/")
    DATABASE_URL = f"{base_url}/{db_name}_test"
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def _ensure_test_database_exists() -> None:
    """Test DB yoksa, aynı sunucudaki 'postgres' bakım veritabanı üzerinden oluşturur"""
    maintenance_url = ASYNC_DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    test_db_name = ASYNC_DATABASE_URL.rsplit("/", 1)[1]

    engine = create_async_engine(maintenance_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        from sqlalchemy import text

        exists = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": test_db_name},
        )
        if exists.scalar() is None:
            await conn.execute(text(f'CREATE DATABASE "{test_db_name}"'))
    await engine.dispose()


test_engine = None
TestSessionLocal = None


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    global test_engine, TestSessionLocal

    await _ensure_test_database_exists()

    test_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    """Her testten önce tabloları temizle — test izolasyonu."""
    if test_engine is not None:
        async with test_engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())
    yield


@pytest_asyncio.fixture
async def test_session():
    assert TestSessionLocal is not None
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
