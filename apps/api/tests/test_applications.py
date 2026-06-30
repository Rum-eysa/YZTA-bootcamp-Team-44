"""Application tests"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_application(client: AsyncClient):
    """Test creating an application"""
    response = await client.post(
        "/applications",
        json={
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "+905555555555",
            "university": "Test University",
            "department": "Computer Engineering",
            "grade": "3",
            "gpa": 3.5,
            "skills": "Python, JavaScript, React",
            "experience": "2 years of web development",
            "motivation": "I want to learn and grow",
            "github_url": "https://github.com/johndoe",
            "linkedin_url": "https://linkedin.com/in/johndoe",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_applications(client: AsyncClient):
    """Test getting applications list"""
    response = await client.get("/applications")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_application_by_id(client: AsyncClient):
    """Test getting a specific application"""
    # Create an application first
    create_response = await client.post(
        "/applications",
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+905555555556",
            "university": "Test University",
            "department": "Computer Engineering",
            "grade": "4",
            "gpa": 3.8,
            "skills": "Python, Django, FastAPI",
            "experience": "3 years of backend development",
            "motivation": "I want to contribute to open source",
        },
    )
    application_id = create_response.json()["id"]
    
    # Get the application
    response = await client.get(f"/applications/{application_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == application_id
    assert data["full_name"] == "Jane Doe"


@pytest.mark.asyncio
async def test_get_application_not_found(client: AsyncClient):
    """Test getting a non-existent application"""
    response = await client.get("/applications/nonexistent-id")
    assert response.status_code == 404
