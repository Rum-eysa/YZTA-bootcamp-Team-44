"""Document compilation endpoints."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.services.compiler import compiler_service

router = APIRouter(prefix="/documents", tags=["Documents"])


async def _collect_uploads(request: Request) -> dict[str, bytes]:
    collected: dict[str, bytes] = {}
    form = await request.form()
    for key, value in form.multi_items():
        if key not in ("file", "files") or not hasattr(value, "read"):
            continue
        name = Path(value.filename).name
        if name:
            collected[name] = await value.read()
    return collected


@router.post("/compile")
async def compile_document(request: Request, main: str | None = None) -> Response:
    file_map = await _collect_uploads(request)
    pdf = await compiler_service.compile(file_map, main_tex=main)

    output_name = "output.pdf"
    if main:
        output_name = Path(main).with_suffix(".pdf").name
    elif len([n for n in file_map if n.endswith(".tex")]) == 1:
        tex_name = next(n for n in file_map if n.endswith(".tex"))
        output_name = Path(tex_name).with_suffix(".pdf").name

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{output_name}"'},
    )
