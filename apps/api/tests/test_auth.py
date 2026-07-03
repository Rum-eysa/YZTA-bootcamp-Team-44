"""Authentication tests"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email"""
    await client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        },
    )

    response = await client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Test user login"""
    # First register a user
    await client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "password": "testpassword123",
            "full_name": "Login User",
        },
    )

    # Then login
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials"""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient):
    """/users/me JWT olmadan erişilemez"""
    response = await client.get("/api/users/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_me_with_token(client: AsyncClient):
    """/users/me sadece geçerli token sahibinin kendi profilini döner"""
    await client.post(
        "/api/auth/register",
        json={
            "email": "me@example.com",
            "password": "testpassword123",
            "full_name": "Me User",
        },
    )
    login = await client.post(
        "/api/auth/login",
        json={"email": "me@example.com", "password": "testpassword123"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_logout_revokes_token(client: AsyncClient):
    """Logout sonrası aynı access token ile /users/me erişilemez"""
    await client.post(
        "/api/auth/register",
        json={
            "email": "logout@example.com",
            "password": "testpassword123",
            "full_name": "Logout User",
        },
    )
    login = await client.post(
        "/api/auth/login",
        json={"email": "logout@example.com", "password": "testpassword123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout_response = await client.post("/api/auth/logout", headers=headers)
    assert logout_response.status_code == 200

    response = await client.get("/api/users/me", headers=headers)
    assert response.status_code == 401
