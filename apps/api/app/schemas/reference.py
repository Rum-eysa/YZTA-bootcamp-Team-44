"""Reference schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReferenceBase(BaseModel):
    name: str = Field(..., max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    contact: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class ReferenceCreate(ReferenceBase):
    pass


class ReferenceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    contact: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class ReferenceResponse(ReferenceBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
