"""Authentication routes"""

from datetime import datetime, timedelta

from app.config import settings
from app.database import get_db
from app.logging_config import get_logger
from app.rate_limit import enforce_rate_limit
from app.schemas.base import SuccessResponse
from app.schemas.user import LogoutRequest, Token, TokenRefresh, UserCreate, UserLogin, UserResponse
from app.services.auth import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    is_token_blacklisted,
)
from app.services.user import authenticate_user, create_user, get_user_by_email, get_user_by_id
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()
logger = get_logger("auth")


async def _blacklist_payload(payload: dict | None) -> None:
    if not payload:
        return
    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti and exp:
        await blacklist_token(jti, datetime.utcfromtimestamp(exp))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user"""
    await enforce_rate_limit(request, suffix="auth_register", limit=10, window_seconds=60)
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await create_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Login user and return JWT tokens"""
    await enforce_rate_limit(request, suffix="auth_login", limit=20, window_seconds=60)
    user = await authenticate_user(db, credentials.email, credentials.password)
    if not user:
        logger.info("auth_login_failed", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.info("auth_login_inactive", user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(data={"sub": user.id})

    logger.info("auth_login_success", user_id=user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token (rotation + blacklist)."""
    payload = decode_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    jti = payload.get("jti", "")
    if jti and await is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        await _blacklist_payload(payload)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Rotate: eski refresh'i hemen geçersiz kıl
    await _blacklist_payload(payload)

    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    )
    new_refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
    }


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    body: LogoutRequest | None = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Logout: access (+ varsa refresh) token jti'lerini Redis blacklist'e alır."""
    access_payload = decode_token(credentials.credentials)
    if not access_payload or access_payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    await _blacklist_payload(access_payload)

    refresh_raw = body.refresh_token if body else None
    if refresh_raw:
        refresh_payload = decode_token(refresh_raw)
        if refresh_payload and refresh_payload.get("type") == "refresh":
            if refresh_payload.get("sub") == access_payload.get("sub"):
                await _blacklist_payload(refresh_payload)

    return SuccessResponse(data=None, message="Logged out")
