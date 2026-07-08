"""Profil iş deneyimi CRUD endpoint testleri (US-013 / US-019).

/api/profiles/me/experiences için create/list/update/delete, validation,
auth ve kullanıcı izolasyonu kapsanır.
"""
import uuid

import pytest
from app.dependencies import get_current_user_id
from app.main import app
from app.models import User, WorkExperience
from httpx import AsyncClient
from sqlalchemy import select


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.pop(get_current_user_id, None)


async def _seed_user(test_session) -> str:
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email=f"exp-{user_id}@example.com", hashed_password="x")
    test_session.add(user)
    await test_session.commit()
    return user_id


def _auth_as(user_id: str) -> None:
    app.dependency_overrides[get_current_user_id] = lambda: user_id


@pytest.mark.asyncio
async def test_create_experience(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    _auth_as(user_id)

    response = await client.post(
        "/api/profiles/me/experiences",
        json={
            "company": "Acme",
            "title": "Backend Developer",
            "start_date": "2022-01-01",
            "end_date": "2024-06-01",
            "description": "API geliştirme",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "Acme"
    assert data["title"] == "Backend Developer"
    assert data["user_id"] == user_id
    assert data["id"]


@pytest.mark.asyncio
async def test_create_experience_open_ended_period(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    _auth_as(user_id)

    response = await client.post(
        "/api/profiles/me/experiences",
        json={"company": "Acme", "title": "Dev", "start_date": "2023-01-01"},
    )

    assert response.status_code == 201
    assert response.json()["end_date"] is None


@pytest.mark.asyncio
async def test_create_experience_missing_required_fields_returns_422(
    client: AsyncClient, test_session
):
    user_id = await _seed_user(test_session)
    _auth_as(user_id)

    response = await client.post("/api/profiles/me/experiences", json={"company": "Acme"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_experiences_returns_only_own(client: AsyncClient, test_session):
    owner_id = await _seed_user(test_session)
    other_id = await _seed_user(test_session)
    test_session.add_all(
        [
            WorkExperience(user_id=owner_id, company="Acme", title="Dev"),
            WorkExperience(user_id=other_id, company="Globex", title="Lead"),
        ]
    )
    await test_session.commit()

    _auth_as(owner_id)
    response = await client.get("/api/profiles/me/experiences")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "Acme"


@pytest.mark.asyncio
async def test_update_experience(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    experience = WorkExperience(user_id=user_id, company="Acme", title="Dev")
    test_session.add(experience)
    await test_session.commit()
    await test_session.refresh(experience)

    _auth_as(user_id)
    response = await client.patch(
        f"/api/profiles/me/experiences/{experience.id}",
        json={"title": "Senior Developer"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Senior Developer"
    assert response.json()["company"] == "Acme"


@pytest.mark.asyncio
async def test_update_experience_of_another_user_returns_404(client: AsyncClient, test_session):
    owner_id = await _seed_user(test_session)
    other_id = await _seed_user(test_session)
    experience = WorkExperience(user_id=owner_id, company="Acme", title="Dev")
    test_session.add(experience)
    await test_session.commit()
    await test_session.refresh(experience)

    _auth_as(other_id)
    response = await client.patch(
        f"/api/profiles/me/experiences/{experience.id}", json={"title": "Hacked"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_experience(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    experience = WorkExperience(user_id=user_id, company="Acme", title="Dev")
    test_session.add(experience)
    await test_session.commit()
    await test_session.refresh(experience)
    experience_id = experience.id

    _auth_as(user_id)
    response = await client.delete(f"/api/profiles/me/experiences/{experience_id}")

    assert response.status_code == 204
    result = await test_session.execute(
        select(WorkExperience).where(WorkExperience.id == experience_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_experience_of_another_user_returns_404(client: AsyncClient, test_session):
    owner_id = await _seed_user(test_session)
    other_id = await _seed_user(test_session)
    experience = WorkExperience(user_id=owner_id, company="Acme", title="Dev")
    test_session.add(experience)
    await test_session.commit()
    await test_session.refresh(experience)

    _auth_as(other_id)
    response = await client.delete(f"/api/profiles/me/experiences/{experience.id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_experiences_require_authentication(client: AsyncClient):
    response = await client.get("/api/profiles/me/experiences")
    assert response.status_code == 403
