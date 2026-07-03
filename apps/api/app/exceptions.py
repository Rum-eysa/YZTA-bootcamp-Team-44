"""Custom Exceptions"""

from typing import Optional

from fastapi import status


class APIException(Exception):
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "API_ERROR",
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(detail)


class ValidationException(APIException):
    def __init__(
        self, detail: str = "Validation failed", errors: Optional[list] = None
    ):
        self.errors = errors or []
        super().__init__(
            detail, status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR"
        )


class AuthenticationException(APIException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED, "AUTH_ERROR")


class ResourceNotFoundException(APIException):
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        detail = f"{resource} not found"
        if resource_id:
            detail += f" (ID: {resource_id})"
        super().__init__(detail, status.HTTP_404_NOT_FOUND, "NOT_FOUND")
