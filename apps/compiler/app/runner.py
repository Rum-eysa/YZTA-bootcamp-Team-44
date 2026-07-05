"""Tectonic subprocess wrapper with XeLaTeX fallback for complex templates."""

import os
import shutil
import signal
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

TIMEOUT = int(os.environ.get("COMPILE_TIMEOUT_SECONDS", "120"))


@dataclass
class CompileResult:
    pdf: bytes | None
    stderr: str
    returncode: int


def _basename(filename: str) -> str:
    return Path(filename).name


def _signal_name(returncode: int) -> str:
    if returncode >= 0:
        return str(returncode)
    sig = -returncode
    try:
        return signal.Signals(sig).name
    except ValueError:
        return f"signal {sig}"


def _run_xelatex(work: Path, main_tex: str, outdir: Path) -> CompileResult:
    stem = Path(main_tex).stem
    pdf_path = outdir / Path(main_tex).with_suffix(".pdf").name
    logs: list[str] = []
    xelatex_cmd = [
        "xelatex",
        "-interaction=nonstopmode",
        "-shell-escape",
        f"-output-directory={outdir}",
        main_tex,
    ]
    proc = subprocess.CompletedProcess(args=xelatex_cmd, returncode=1)

    for _ in range(2):
        proc = subprocess.run(
            xelatex_cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd=str(work),
        )
        logs.append((proc.stdout or "") + (proc.stderr or ""))

    bcf = outdir / f"{stem}.bcf"
    if bcf.exists() and shutil.which("biber"):
        biber = subprocess.run(
            ["biber", stem],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd=str(outdir),
        )
        logs.append((biber.stdout or "") + (biber.stderr or ""))
        proc = subprocess.run(
            xelatex_cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd=str(work),
        )
        logs.append((proc.stdout or "") + (proc.stderr or ""))

    stderr = "\n".join(logs).strip()
    if pdf_path.exists():
        return CompileResult(pdf=pdf_path.read_bytes(), stderr="", returncode=0)

    return CompileResult(pdf=None, stderr=stderr, returncode=proc.returncode)


def _run_tectonic(work: Path, tex_path: Path, outdir: Path) -> CompileResult:
    env = {**os.environ, "SOURCE_DATE_EPOCH": os.environ.get("SOURCE_DATE_EPOCH", "1700000000")}
    proc = subprocess.run(
        ["tectonic", str(tex_path), "--outdir", str(outdir)],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        cwd=str(work),
        env=env,
    )
    stderr = (proc.stderr or "") + (proc.stdout or "")
    if proc.returncode < 0:
        stderr = f"Tectonic crashed ({_signal_name(proc.returncode)}).\n{stderr}"

    pdf_path = outdir / tex_path.with_suffix(".pdf").name
    if proc.returncode == 0 and pdf_path.exists():
        return CompileResult(pdf=pdf_path.read_bytes(), stderr="", returncode=0)

    return CompileResult(pdf=None, stderr=stderr.strip(), returncode=proc.returncode)


def compile_project(files: dict[str, bytes], main_tex: str) -> CompileResult:
    main_tex = _basename(main_tex)

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for name, content in files.items():
            safe = _basename(name)
            if safe:
                (work / safe).write_bytes(content)

        tex_path = work / main_tex
        if not tex_path.exists():
            return CompileResult(
                pdf=None,
                stderr=f"Main file not found: {main_tex}",
                returncode=1,
            )

        outdir = work / "out"
        outdir.mkdir()

        tectonic_result = _run_tectonic(work, tex_path, outdir)
        if tectonic_result.pdf is not None:
            return tectonic_result

        if shutil.which("xelatex"):
            xelatex_result = _run_xelatex(work, main_tex, outdir)
            if xelatex_result.pdf is not None:
                return xelatex_result
            combined = f"{tectonic_result.stderr}\n\n--- XeLaTeX fallback ---\n{xelatex_result.stderr}"
            return CompileResult(pdf=None, stderr=combined.strip(), returncode=xelatex_result.returncode)

        return tectonic_result


def resolve_main_tex(files: dict[str, bytes], main: str | None) -> str | None:
    tex_files = sorted(name for name in files if name.endswith(".tex"))
    if not tex_files:
        return None
    if main:
        main = _basename(main)
        return main if main in files else None
    if len(tex_files) == 1:
        return tex_files[0]
    return None
