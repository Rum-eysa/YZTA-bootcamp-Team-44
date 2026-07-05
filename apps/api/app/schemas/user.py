"""User-related schemas"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=255, description="User full name")


class UserCreate(UserBase):
    """Schema for user registration"""

    password: str = Field(
        ..., min_length=8, max_length=100, description="User password"
    )


class UserUpdate(BaseModel):
    """Schema for user profile update"""

    full_name: Optional[str] = Field(None, max_length=255, description="User full name")
    email: Optional[EmailStr] = Field(None, description="User email address")


class UserInDB(UserBase):
    """Schema for user in database"""

    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


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
