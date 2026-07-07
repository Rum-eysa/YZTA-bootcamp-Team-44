"""Social link schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SocialLinkBase(BaseModel):
    platform: str = Field(..., max_length=100)
    url: str = Field(..., max_length=1000)


class SocialLinkCreate(SocialLinkBase):
    pass


class SocialLinkUpdate(BaseModel):
    platform: Optional[str] = Field(None, max_length=100)
    url: Optional[str] = Field(None, max_length=1000)


class SocialLinkResponse(SocialLinkBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

