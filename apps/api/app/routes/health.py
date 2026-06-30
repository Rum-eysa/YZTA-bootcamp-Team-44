"""Health check endpoints"""

from typing import Any

from fastapi import APIRouter

router = APIRouter(tags=["Health"], prefix="/health")


@router.get("", response_model=dict[str, Any])
async def health_check() -> dict[str, Any]:
    """
    Application health check endpoint.
    
    Returns:
        dict: Service health status information
    """
    return {
        "status": "healthy",
        "service": "YZTA Bootcamp API",
        "version": "1.0.0",
    }


@router.get("/ready", response_model=dict[str, str])
async def readiness_probe() -> dict[str, str]:
    """
    Readiness probe for Kubernetes / orchestration systems.
    
    Returns:
        dict: Readiness status
    """
    return {"status": "ready"}
