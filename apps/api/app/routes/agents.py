"""Agent system routes for future AI agent integration"""

import json
from typing import Any

from app.schemas.base import SuccessResponse
from app.services.agent import agent_service
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/tasks", status_code=status.HTTP_202_ACCEPTED)
async def create_agent_task(task_type: str, payload: Any = None):
    """Create a new agent task with a payload that can be provided as JSON or a simple value."""
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"value": payload}
    elif payload is None:
        payload = {}

    result = await agent_service.create_task(
        task_type=task_type,
        payload=payload if isinstance(payload, dict) else {"value": payload},
    )

    return SuccessResponse(
        data={"task_id": result.id, "status": result.status},
        message="Agent task created successfully",
    )


@router.get("/tasks/{task_id}")
async def get_agent_task_status(task_id: str):
    """Get agent task status."""
    status_info = await agent_service.get_task_status(task_id)

    if not status_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return status_info


@router.get("/status")
async def get_agent_system_status():
    """Get agent system status."""
    return {
        "status": "operational",
        "message": "Agent foundation services are available",
        "features": [
            "Base agent execution lifecycle",
            "Structured logging",
            "Context manager memory (US-017)",
            "Retry scaffolding",
            "Task tracking",
        ],
    }
