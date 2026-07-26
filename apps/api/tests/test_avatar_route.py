"""Profil avatar upload/delete endpoint smoke testleri."""
import uuid
from unittest.mock import MagicMock, patch

import pytest
from app.dependencies import get_current_user_id
from app.main import app
from app.models import User
from httpx import AsyncClient


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.pop(get_current_user_id, None)


async def _seed_user(test_session) -> str:
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email=f"avatar-{user_id}@example.com", hashed_password="x")
    test_session.add(user)
    await test_session.commit()
    return user_id


def _auth_as(user_id: str) -> None:
    app.dependency_overrides[get_current_user_id] = lambda: user_id


@pytest.mark.asyncio
async def test_upload_avatar_saves_url(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    _auth_as(user_id)

    fake_storage = MagicMock()
    fake_storage.upload_avatar.return_value = (
        f"http://localhost:9000/bucket/avatars/{user_id}/x.jpg"
    )

    with patch("app.routes.profiles.get_storage_service", return_value=fake_storage):
        response = await client.post(
            "/api/profiles/me/avatar",
            files={"file": ("photo.jpg", b"\xff\xd8\xfffakejpeg", "image/jpeg")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["avatar_url"] == f"http://localhost:9000/bucket/avatars/{user_id}/x.jpg"
    fake_storage.upload_avatar.assert_called_once()


@pytest.mark.asyncio
async def test_upload_avatar_rejects_non_image(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    _auth_as(user_id)

    response = await client.post(
        "/api/profiles/me/avatar",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_avatar_clears_url(client: AsyncClient, test_session):
    user_id = await _seed_user(test_session)
    user = await test_session.get(User, user_id)
    user.avatar_url = "http://localhost:9000/bucket/avatars/x.jpg"
    await test_session.commit()
    _auth_as(user_id)

    response = await client.delete("/api/profiles/me/avatar")
    assert response.status_code == 200
    assert response.json()["avatar_url"] is None
