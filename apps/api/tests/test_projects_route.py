"""Profil proje CRUD endpoint testleri (US-013 / US-020).

/api/profiles/me/projects için create/list/update/delete, tech_stack
serileştirme, url, auth ve kullanıcı izolasyonu kapsanır.
"""
import json
import uuid

import pytest
from app.dependencies import get_current_user_id
from app.main import app
from app.models import Project, User
from httpx import AsyncClient
from sqlalchemy import select


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.pop(get_current_user_id, None)


async def _seed_user(test_session) -> str:
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email=f"proj-{user_id}@example.com", hashed_password="x")
    test_session.add(user)
    await test_session.commit()
    return user_id


def _auth_as(user_id: str) -> None:
    app.dependency_overrides[get_current_user_id] = lambda: user_id


@pytest.mark.asyncio
async def test_create_project_with_tech_stack(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    _auth_as(user_id)

    response = await client.post(
        "/api/profiles/me/projects",
        json={
            "title": "CareerTrack",
            "description": "AI platformu",
            "tech_stack": ["Python", "Next.js"],
            "url": "https://github.com/example/careertrack",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "CareerTrack"
    assert data["tech_stack"] == ["Python", "Next.js"]
    assert data["url"] == "https://github.com/example/careertrack"
    assert data["user_id"] == user_id


@pytest.mark.asyncio
async def test_create_project_persists_tech_stack_as_json(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    _auth_as(user_id)

    response = await client.post(
        "/api/profiles/me/projects",
        json={"title": "P", "tech_stack": ["Go", "gRPC"]},
    )
    project_id = response.json()["id"]

    result = await test_session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one()
    assert json.loads(project.tech_stack) == ["Go", "gRPC"]


@pytest.mark.asyncio
async def test_create_project_without_optional_fields(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    _auth_as(user_id)

    response = await client.post("/api/profiles/me/projects", json={"title": "Minimal"})

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal"
    assert data["url"] is None


@pytest.mark.asyncio
async def test_create_project_missing_title_returns_422(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    _auth_as(user_id)

    response = await client.post("/api/profiles/me/projects", json={"description": "no title"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_projects_returns_only_own(client: AsyncClient, test_session):
    owner_id = await _seed_user(test_session)
    other_id = await _seed_user(test_session)
    test_session.add_all(
        [
            Project(user_id=owner_id, title="Mine", tech_stack=json.dumps(["Rust"])),
            Project(user_id=other_id, title="Theirs"),
        ]
    )
    await test_session.commit()

    _auth_as(owner_id)
    response = await client.get("/api/profiles/me/projects")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Mine"
    assert data[0]["tech_stack"] == ["Rust"]


@pytest.mark.asyncio
async def test_update_project_tech_stack(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    project = Project(user_id=user_id, title="P", tech_stack=json.dumps(["Python"]))
    test_session.add(project)
    await test_session.commit()
    await test_session.refresh(project)

    _auth_as(user_id)
    response = await client.patch(
        f"/api/profiles/me/projects/{project.id}",
        json={"tech_stack": ["Python", "FastAPI"]},
    )

    assert response.status_code == 200
    assert response.json()["tech_stack"] == ["Python", "FastAPI"]


@pytest.mark.asyncio
async def test_update_project_of_another_user_returns_404(client: AsyncClient, test_session):
    owner_id = await _seed_user(test_session)
    other_id = await _seed_user(test_session)
    project = Project(user_id=owner_id, title="P")
    test_session.add(project)
    await test_session.commit()
    await test_session.refresh(project)

    _auth_as(other_id)
    response = await client.patch(
        f"/api/profiles/me/projects/{project.id}", json={"title": "Hacked"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    project = Project(user_id=user_id, title="P")
    test_session.add(project)
    await test_session.commit()
    await test_session.refresh(project)
    project_id = project.id

    _auth_as(user_id)
    response = await client.delete(f"/api/profiles/me/projects/{project_id}")

    assert response.status_code == 204
    result = await test_session.execute(select(Project).where(Project.id == project_id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_project_of_another_user_returns_404(client: AsyncClient, test_session):
    owner_id = await _seed_user(test_session)
    other_id = await _seed_user(test_session)
    project = Project(user_id=owner_id, title="P")
    test_session.add(project)
    await test_session.commit()
    await test_session.refresh(project)

    _auth_as(other_id)
    response = await client.delete(f"/api/profiles/me/projects/{project.id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_projects_require_authentication(client: AsyncClient):
    response = await client.get("/api/profiles/me/projects")
    assert response.status_code == 403
