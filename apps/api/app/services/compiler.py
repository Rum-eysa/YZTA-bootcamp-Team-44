"""Document compilation proxy to the compiler service."""

import httpx
from app.config import settings
from app.exceptions import APIException


class CompilerService:
    async def compile(
        self,
        files: dict[str, bytes],
        main_tex: str | None = None,
    ) -> bytes:
        url = f"{settings.COMPILER_URL.rstrip('/')}/compile"
        multipart = [
            ("files", (name, content, "application/octet-stream"))
            for name, content in files.items()
        ]
        params = {"main": main_tex} if main_tex else {}

        try:
            async with httpx.AsyncClient(timeout=settings.COMPILER_TIMEOUT_SECONDS) as client:
                response = await client.post(url, files=multipart, params=params)
        except httpx.ConnectError as exc:
            raise APIException(
                "Compiler service unavailable",
                status_code=503,
                error_code="COMPILER_UNAVAILABLE",
            ) from exc

        if response.status_code == 200:
            return response.content

        detail = response.json().get("detail", "Compilation failed")
        if isinstance(detail, dict):
            message = detail.get("message", "Compilation failed")
        else:
            message = str(detail)

        raise APIException(message, status_code=response.status_code, error_code="COMPILE_ERROR")


compiler_service = CompilerService()
