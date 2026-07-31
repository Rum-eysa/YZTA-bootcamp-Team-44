"""CV dosya indirme: JWT + sahiplik zorunlu; başka kullanıcı / anonim erişemez."""

import uuid

import pytest
from app.dependencies import get_current_user_id
from app.main import app
from app.models import Document, JobListing, User
from httpx import AsyncClient


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.pop(get_current_user_id, None)


async def _seed(test_session, user_id: str, other: bool = False):
    email = f"{'other' if other else 'owner'}-{user_id}@example.com"
    user = User(id=user_id, email=email, hashed_password="x")
    test_session.add(user)
    await test_session.commit()

    listing = JobListing(
        id=str(uuid.uuid4()),
        created_by=user_id,
        title="Dev",
        company="Acme",
        raw_text="x" * 60,
        analysis_status="completed",
    )
    test_session.add(listing)
    await test_session.commit()

    doc = Document(
        id=str(uuid.uuid4()),
        user_id=user_id,
        listing_id=listing.id,
        doc_type="cv",
        cv_url="http://localhost:9000/cv-documents/cv/fake.pdf",
    )
    test_session.add(doc)
    await test_session.commit()
    return doc


@pytest.mark.asyncio
async def test_document_file_requires_auth(client: AsyncClient, test_session):
    owner_id = str(uuid.uuid4())
    doc = await _seed(test_session, owner_id)
    response = await client.get(f"/api/documents/{doc.id}/file")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_document_file_rejects_other_user(client: AsyncClient, test_session, monkeypatch):
    owner_id = str(uuid.uuid4())
    other_id = str(uuid.uuid4())
    doc = await _seed(test_session, owner_id)
    other = User(id=other_id, email=f"intruder-{other_id}@example.com", hashed_password="x")
    test_session.add(other)
    await test_session.commit()

    app.dependency_overrides[get_current_user_id] = lambda: other_id
    response = await client.get(f"/api/documents/{doc.id}/file")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_document_file_streams_for_owner(client: AsyncClient, test_session, monkeypatch):
    owner_id = str(uuid.uuid4())
    doc = await _seed(test_session, owner_id)
    app.dependency_overrides[get_current_user_id] = lambda: owner_id

    class _FakeStorage:
        def download_bytes(self, url: str):
            return b"%PDF-1.4 fake"

    monkeypatch.setattr("app.routes.documents.get_storage_service", lambda: _FakeStorage())

    response = await client.get(f"/api/documents/{doc.id}/file")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.content.startswith(b"%PDF")
    assert "no-store" in response.headers.get("cache-control", "")
