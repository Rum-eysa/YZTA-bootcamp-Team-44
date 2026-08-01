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
    def __init__(self, detail: str = "Validation failed", errors: Optional[list] = None):
        self.errors = errors or []
        super().__init__(detail, status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR")


class AuthenticationException(APIException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED, "AUTH_ERROR")


class ResourceNotFoundException(APIException):
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        detail = f"{resource} not found"
        if resource_id:
            detail += f" (ID: {resource_id})"
        super().__init__(detail, status.HTTP_404_NOT_FOUND, "NOT_FOUND")


class GeminiAPIException(APIException):
    """Gemini API çağrısı kota/limit/geçici hata nedeniyle başarısız oldu"""

    def __init__(self, detail: str = "AI service temporarily unavailable"):
        super().__init__(detail, status.HTTP_503_SERVICE_UNAVAILABLE, "GEMINI_API_ERROR")


class GeminiQuotaException(GeminiAPIException):
    """Gemini günlük/dakikalık kota (429) tükendi - kullanıcıya net ve
    'sonra tekrar dene' yönlendirmeli mesaj gösterilmeli (#100). retry_after
    saniye cinsindendir; HTTP 429 + Retry-After başlığı için kullanılır."""

    def __init__(
        self,
        detail: str = (
            "Yapay zeka servisi günlük kullanım limitine ulaştı. "
            "Lütfen bir süre sonra tekrar deneyin."
        ),
        retry_after: Optional[int] = None,
    ):
        self.retry_after = retry_after
        # APIException.__init__ çağrısını atlayıp doğrudan alanları set ediyoruz ki
        # 429 status'u ve özel error_code'u koruyalım.
        APIException.__init__(self, detail, status.HTTP_429_TOO_MANY_REQUESTS, "GEMINI_QUOTA_ERROR")
