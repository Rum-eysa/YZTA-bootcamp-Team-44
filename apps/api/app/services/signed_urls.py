"""API yanıtlarında depolama URL'lerini istemciye sızdırmadan erişim yolu üretir.

CV/avatar için MinIO/presigned URL dönülmez — JWT korumalı API path kullanılır.
"""

from typing import Any, Optional

from app.models import User
from app.schemas.user import UserResponse


def document_file_path(document_id: str) -> str:
    """Tarayıcının Bearer token ile çağıracağı CV dosya yolu."""
    return f"/api/documents/{document_id}/file"


def avatar_file_path() -> str:
    """Oturum açmış kullanıcının avatar dosya yolu."""
    return "/api/profiles/me/avatar/file"


def user_response_with_signed_avatar(user: User) -> UserResponse:
    data = UserResponse.model_validate(user)
    # Depodaki gerçek URL'yi sızdırma; yalnızca API proxy yolu
    data.avatar_url = avatar_file_path() if user.avatar_url else None
    return data


def sign_cv_url_in_dict(payload: dict[str, Any], document_id: Optional[str] = None) -> dict[str, Any]:
    if payload.get("cv_url") and document_id:
        payload = {**payload, "cv_url": document_file_path(document_id)}
    elif payload.get("cv_url"):
        # document_id yoksa ham MinIO URL'sini gizle
        payload = {**payload, "cv_url": None}
    return payload
