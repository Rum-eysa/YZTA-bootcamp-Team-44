"""Custom Middleware"""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        try:
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info(
                "HTTP request",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )
            response.headers["X-Process-Time"] = str(duration)
            return response
        except Exception as exc:
            duration = time.time() - start_time
            logger.error(
                "HTTP request failed",
                request_id=request_id,
                method=request.method,
                error=str(exc),
                exc_info=True,
            )
            raise
