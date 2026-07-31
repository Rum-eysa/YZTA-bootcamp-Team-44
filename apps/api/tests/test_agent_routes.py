import pytest
from httpx import AsyncClient


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    await client.post(
        "/api/auth/register",
        json={
            "email": "agent-route@example.com",
            "password": "testpassword123",
            "full_name": "Agent User",
        },
    )
    login = await client.post(
        "/api/auth/login",
        json={"email": "agent-route@example.com", "password": "testpassword123"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.mark.asyncio
async def test_agent_task_creation_and_status_flow(client: AsyncClient):
    headers = await _auth_headers(client)
    response = await client.post(
        "/api/agents/tasks",
        params={"task_type": "analyze", "payload": {"text": "demo"}},
        headers=headers,
    )
    assert response.status_code == 202
    payload = response.json()
    task_id = payload["data"]["task_id"]

    status_response = await client.get(f"/api/agents/tasks/{task_id}", headers=headers)
    assert status_response.status_code == 200
    status_payload = status_response.json()
    assert status_payload["task_id"] == task_id
    assert status_payload["status"] == "processing"


@pytest.mark.asyncio
async def test_agent_routes_reject_unauthenticated(client: AsyncClient):
    response = await client.post(
        "/api/agents/tasks",
        params={"task_type": "analyze", "payload": {"text": "demo"}},
    )
    assert response.status_code in (401, 403)
