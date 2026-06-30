"""Base schemas for common responses"""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    """Health check response schema"""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")

    model_config = ConfigDict(json_schema_extra={"example": {"status": "healthy", "service": "YZTA API", "version": "1.0.0"}})


class ErrorResponse(BaseModel):
    """Standard error response schema"""

    detail: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    model_config = ConfigDict(json_schema_extra={"example": {"detail": "Not found", "error_code": "NOT_FOUND", "request_id": "uuid"}})


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response schema"""

    data: list[T] = Field(..., description="Response data")
    total: int = Field(..., description="Total count")
    page: int = Field(default=1, ge=1, description="Current page")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")
    has_more: bool = Field(..., description="Whether more items exist")


class SuccessResponse(BaseModel, Generic[T]):
    """Generic success response schema"""

    success: bool = Field(default=True, description="Operation success status")
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Optional success message")
