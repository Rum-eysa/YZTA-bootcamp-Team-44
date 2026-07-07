"""Language schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LanguageBase(BaseModel):
    name: str = Field(..., max_length=100)
    level: Optional[str] = Field(None, max_length=100)


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    level: Optional[str] = Field(None, max_length=100)


class LanguageResponse(LanguageBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

