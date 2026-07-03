"""LaTeX compiler HTTP service."""

import subprocess
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response

from app.runner import compile_project, resolve_main_tex

app = FastAPI(title="YZTA Compiler", version="1.0.0")


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


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/compile")
async def compile_document(request: Request, main: str | None = None):
    file_map = await _collect_uploads(request)
    if not file_map:
        raise HTTPException(status_code=400, detail="No files uploaded")

    main_tex = resolve_main_tex(file_map, main)
    if not main_tex:
        tex_count = sum(1 for name in file_map if name.endswith(".tex"))
        if tex_count == 0:
            raise HTTPException(status_code=400, detail="Expected at least one .tex file")
        raise HTTPException(
            status_code=400,
            detail="Multiple .tex files: specify ?main=filename.tex",
        )

    try:
        result = compile_project(file_map, main_tex=main_tex)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Compilation timed out")

    if result.pdf is None:
        raise HTTPException(
            status_code=422,
            detail={"message": "Compilation failed", "stderr": result.stderr},
        )

    output_name = Path(main_tex).with_suffix(".pdf").name
    return Response(
        content=result.pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{output_name}"'},
    )
