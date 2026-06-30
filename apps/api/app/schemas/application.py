"""Application/Staj başvuru schemas"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ApplicationBase(BaseModel):
    """Base application schema"""
    
    full_name: str = Field(..., min_length=2, max_length=255, description="Applicant full name")
    email: str = Field(..., description="Applicant email")
    phone: str = Field(..., description="Applicant phone number")
    university: str = Field(..., description="University name")
    department: str = Field(..., description="Department/Faculty")
    grade: str = Field(..., description="Current grade (1, 2, 3, 4)")
    gpa: float = Field(..., ge=0.0, le=4.0, description="GPA score")
    skills: str = Field(..., description="Skills and technologies")
    experience: str = Field(..., description="Previous experience")
    motivation: str = Field(..., description="Motivation for applying")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")


class ApplicationCreate(ApplicationBase):
    """Schema for creating a new application"""
    
    user_id: Optional[str] = Field(None, description="User ID (if authenticated)")


class ApplicationUpdate(BaseModel):
    """Schema for updating an application"""
    
    status: Optional[str] = Field(None, description="Application status")
    ai_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="AI analysis score")
    ai_feedback: Optional[str] = Field(None, description="AI analysis feedback")
    reviewer_notes: Optional[str] = Field(None, description="Reviewer notes")


class ApplicationInDB(ApplicationBase):
    """Schema for application in database"""
    
    id: str
    user_id: Optional[str]
    status: str
    ai_score: Optional[float]
    ai_feedback: Optional[str]
    reviewer_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationResponse(ApplicationInDB):
    """Schema for application response"""
    
    pass


class AIAnalysisRequest(BaseModel):
    """Schema for AI analysis request"""
    
    application_id: str = Field(..., description="Application ID to analyze")


class AIAnalysisResponse(BaseModel):
    """Schema for AI analysis response"""
    
    application_id: str
    score: float = Field(..., ge=0.0, le=100.0, description="Analysis score (0-100)")
    feedback: str = Field(..., description="Detailed feedback")
    strengths: list[str] = Field(default_factory=list, description="Identified strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Identified weaknesses")
    recommendation: str = Field(..., description="Overall recommendation")
