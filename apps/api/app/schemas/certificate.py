"""Certificate schemas"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CertificateBase(BaseModel):
    title: str = Field(..., max_length=255)
    issuer: Optional[str] = Field(None, max_length=255)
    issue_date: Optional[date] = None
    url: Optional[str] = Field(None, max_length=1000)


class CertificateCreate(CertificateBase):
    pass


class CertificateUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    issuer: Optional[str] = Field(None, max_length=255)
    issue_date: Optional[date] = None
    url: Optional[str] = Field(None, max_length=1000)


class CertificateResponse(CertificateBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

