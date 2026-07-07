"""User-related schemas"""

import json
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=50, description="User full name")


class UserCreate(UserBase):
    """Schema for user registration"""

    password: str = Field(..., min_length=8, max_length=100, description="User password")


class UserProfileUpdate(BaseModel):
    """Schema for updating agent-facing profile fields (skills, ton, seniority...)"""

    target_position: Optional[str] = Field(None, max_length=50)
    seniority: Optional[str] = Field(None, description="junior/mid/senior")
    experience_years: Optional[float] = Field(None, ge=0)
    skills: Optional[List[str]] = Field(None, description="Beceri listesi")
    experience_summary: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=50)
    birth_year: Optional[int] = Field(None, ge=1900, le=2100)
    tone_preference: Optional[str] = Field(None, description="professional/casual/confident")
    gender: Optional[str] = Field(None, description="Cinsiyet")
    nationality: Optional[str] = Field(None, description="Uyruk")
    driver_license: Optional[str] = Field(None, description="Sürücü belgesi")
    military_status: Optional[str] = Field(None, description="Askerlik durumu")


class UserUpdate(UserProfileUpdate):
    """Schema for user profile update"""

    full_name: Optional[str] = Field(None, max_length=50, description="User full name")
    email: Optional[EmailStr] = Field(None, description="User email address")


class UserInDB(UserBase):
    """Schema for user in database"""

    id: str
    is_active: bool
    target_position: Optional[str] = None
    seniority: Optional[str] = None
    experience_years: Optional[float] = None
    skills: Optional[List[str]] = None
    experience_summary: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    birth_year: Optional[int] = None
    tone_preference: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    driver_license: Optional[str] = None
    military_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("skills", mode="before")
    @classmethod
    def parse_skills(cls, v):
        """DB'de skills Text(JSON string) olarak tutulur, API'de List[str] döner"""
        if isinstance(v, str):
            return json.loads(v) if v else []
        return v


class UserResponse(UserInDB):
    """Schema for user response (excludes sensitive data)"""

    pass


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """Schema for JWT token response"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenRefresh(BaseModel):
    """Schema for token refresh"""

    refresh_token: str = Field(..., description="Refresh token")
