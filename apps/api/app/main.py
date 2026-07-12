"""FastAPI Application - Production Ready"""

import logging
from contextlib import asynccontextmanager
from typing import Callable
from urllib.parse import urlparse

from app.config import settings
from app.exceptions import APIException
from app.logging_config import setup_logging
from app.middleware import LoggingMiddleware, RequestIDMiddleware
from app.observability import capture_exception, init_sentry
from app.routes import (
    agents,
    analysis,
    auth,
    cover_letter,
    cv_generation,
    health,
    listings,
    match,
    orchestrator,
    profiles,
    users,
)
from app.services.storage import get_storage_service
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

logger = setup_logging(log_level=getattr(logging, settings.LOG_LEVEL.upper()))
init_sentry()


def _cors_headers(request: Request) -> dict[str, str]:
    origin = request.headers.get("origin")
    allowed = {o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()}
    if origin and origin in allowed:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Vary": "Origin",
        }
    return {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API starting", environment=settings.ENVIRONMENT)
    if settings.ENVIRONMENT != "test":
        get_storage_service().ensure_bucket()
    yield
    logger.info("API shutting down")


app = FastAPI(
    title="YZTA Bootcamp API",
    description="Yapay zeka destekli staj başvuru platformu",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
)

allowed_hosts = ["localhost", "127.0.0.1", "test", "testserver"]

if settings.ENVIRONMENT not in ("test",) and not settings.DEBUG:
    parsed_hosts = [
        host.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if (host := urlparse(origin).netloc) or origin.strip()
    ]
    allowed_hosts.extend(parsed_hosts)

allowed_hosts = list(dict.fromkeys(host for host in allowed_hosts if host))

app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

app.add_middleware(GZipMiddleware, minimum_size=1000)

cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(profiles.router, prefix="/api/profiles")
app.include_router(agents.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(listings.router, prefix="/api/listings")
app.include_router(cover_letter.router, prefix="/api")
app.include_router(cv_generation.router, prefix="/api")
app.include_router(match.router, prefix="/api")
app.include_router(orchestrator.router, prefix="/api")


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
            "request_id": getattr(request.state, "request_id", None),
        },
        headers=_cors_headers(request),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": "Request validation failed", "errors": exc.errors()}),
        headers=_cors_headers(request),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", path=request.url.path, error=str(exc), exc_info=True)
    capture_exception(exc)
    content: dict = {"detail": "Internal server error"}
    if settings.DEBUG:
        content["error"] = str(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content,
        headers=_cors_headers(request),
    )


@app.middleware("http")
async def add_security_headers(request: Request, call_next: Callable):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.get("/", tags=["Info"])
async def root():
    return {
        "name": "YZTA Bootcamp API",
        "version": "1.0.0",
        "description": "Yapay zeka destekli staj başvuru platformu",
        "docs": "/docs" if settings.DEBUG else None,
    }


@app.get("/status", tags=["Info"])
async def status_check():
    return {"status": "online", "version": "1.0.0", "environment": settings.ENVIRONMENT}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
