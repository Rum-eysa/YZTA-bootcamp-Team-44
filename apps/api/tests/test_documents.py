from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

SAMPLE_PDF = b"%PDF-1.4 minimal"


@pytest.mark.asyncio
async def test_compile_document(client: AsyncClient):
    with patch(
        "app.routes.documents.compiler_service.compile",
        new=AsyncMock(return_value=SAMPLE_PDF),
    ):
        response = await client.post(
            "/documents/compile",
            files={"file": ("sample.tex", r"\documentclass{article}", "application/x-tex")},
        )

    assert response.status_code == 200
    assert response.content == SAMPLE_PDF


@pytest.mark.asyncio
async def test_compile_multiple_files(client: AsyncClient):
    with patch(
        "app.routes.documents.compiler_service.compile",
        new=AsyncMock(return_value=SAMPLE_PDF),
    ) as mock_compile:
        response = await client.post(
            "/documents/compile?main=serkan.tex",
            files=[
                ("files", ("serkan.tex", r"\documentclass{altacv}", "application/x-tex")),
                ("files", ("altacv.cls", r"\ProvidesClass{altacv}", "text/plain")),
            ],
        )

    assert response.status_code == 200
    mock_compile.assert_awaited_once()
    assert "altacv.cls" in mock_compile.await_args.args[0]


@pytest.mark.asyncio
async def test_compile_unavailable(client: AsyncClient):
    from app.exceptions import APIException

    with patch(
        "app.routes.documents.compiler_service.compile",
        new=AsyncMock(
            side_effect=APIException("Compiler service unavailable", 503, "COMPILER_UNAVAILABLE")
        ),
    ):
        response = await client.post(
            "/documents/compile",
            files={"file": ("sample.tex", r"\documentclass{article}", "application/x-tex")},
        )

    assert response.status_code == 503
