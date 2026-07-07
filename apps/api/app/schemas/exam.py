"""Exam schemas"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExamBase(BaseModel):
    name: str = Field(..., max_length=255)
    score: Optional[str] = Field(None, max_length=100)
    exam_date: Optional[date] = None
    description: Optional[str] = None


class ExamCreate(ExamBase):
    pass


class ExamUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    score: Optional[str] = Field(None, max_length=100)
    exam_date: Optional[date] = None
    description: Optional[str] = None


class ExamResponse(ExamBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
