"""Application/Staj başvuru routes"""
from typing import Optional

from app.database import get_db
from app.schemas.application import (
    AIAnalysisResponse,
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)
from app.schemas.base import PaginatedResponse
from app.services.application import (
    analyze_application_with_ai,
    create_application,
    get_all_applications,
    get_application_by_id,
    get_applications_by_user,
    update_application,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application_endpoint(
    application_data: ApplicationCreate,
    user_id: Optional[str] = Query(None, description="User ID if authenticated"),
    db: AsyncSession = Depends(get_db),
):
    """Create a new internship application"""
    if user_id:
        application_data.user_id = user_id

    application = await create_application(db, application_data)
    return application


@router.get("", response_model=PaginatedResponse[ApplicationResponse])
async def get_applications(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    db: AsyncSession = Depends(get_db),
):
    """Get applications (filtered by user if user_id provided)"""
    if user_id:
        applications = await get_applications_by_user(db, user_id, skip, limit)
        total = len(applications)
    else:
        applications = await get_all_applications(db, skip, limit)
        total = len(applications)

    return PaginatedResponse(
        data=applications,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        has_more=skip + limit < total,
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: str, db: AsyncSession = Depends(get_db)):
    """Get application by ID"""
    application = await get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return application


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application_endpoint(
    application_id: str,
    application_data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update application (admin only)"""
    application = await update_application(db, application_id, application_data)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return application


@router.post("/{application_id}/analyze", response_model=AIAnalysisResponse)
async def analyze_application(application_id: str, db: AsyncSession = Depends(get_db)):
    """Analyze application using AI"""
    application = await get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    analysis = await analyze_application_with_ai(application)

    # Update application with AI analysis
    await update_application(
        db,
        application_id,
        ApplicationUpdate(
            ai_score=analysis["score"],
            ai_feedback=analysis["feedback"],
        ),
    )

    return AIAnalysisResponse(application_id=application_id, **analysis)
