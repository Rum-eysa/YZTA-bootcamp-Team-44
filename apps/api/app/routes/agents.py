"""Agent system routes for future AI agent integration"""
from fastapi import APIRouter, HTTPException, status

from app.schemas.base import SuccessResponse
from app.services.agent import agent_service

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/tasks", status_code=status.HTTP_202_ACCEPTED)
async def create_agent_task(task_type: str, payload: dict):
    """
    Create a new agent task (placeholder for future implementation)

    This endpoint is prepared for future agent system integration.
    Currently returns a placeholder response.
    """
    result = await agent_service.create_task(
        task_type=task_type,
        payload=payload,
    )

    return SuccessResponse(
        data={"task_id": result.id, "status": "pending"},
        message="Agent system not yet integrated - task created but not processed",
    )


@router.get("/tasks/{task_id}")
async def get_agent_task_status(task_id: str):
    """
    Get agent task status (placeholder for future implementation)

    This endpoint is prepared for future agent system integration.
    """
    status_info = await agent_service.get_task_status(task_id)

    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return status_info


@router.get("/status")
async def get_agent_system_status():
    """
    Get agent system status (placeholder for future implementation)

    This endpoint is prepared for future agent system integration.
    """
    return {
        "status": "not_implemented",
        "message": "Agent system integration planned for future release",
        "planned_features": [
            "LangChain/CrewAI integration",
            "Multi-agent workflows",
            "Automated application processing",
            "Smart notifications",
            "Decision support system",
        ],
    }
