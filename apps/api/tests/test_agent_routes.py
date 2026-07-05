import pytest
from app.main import app
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_agent_task_creation_and_status_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/agents/tasks",
            params={"task_type": "analyze", "payload": {"text": "demo"}},
        )
        assert response.status_code == 202
        payload = response.json()
        task_id = payload["data"]["task_id"]

        status_response = await client.get(f"/agents/tasks/{task_id}")
        assert status_response.status_code == 200
        status_payload = status_response.json()
        assert status_payload["task_id"] == task_id
        assert status_payload["status"] == "processing"
