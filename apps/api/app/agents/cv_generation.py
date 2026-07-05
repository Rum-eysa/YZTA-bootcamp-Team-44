"""CV Ajanı: profil + ilan eşleştirmesi -> derlenmiş LaTeX PDF CV.

En riskli adım (Tectonic Docker'da çalışıyor mu) - `apps/api/Dockerfile`'da amd64
emülasyonu + debian:trixie-slim ile çözüldü (Apple Silicon'da arm64 Tectonic binary'si
yok, glibc uyumsuzluğu vardı). Derleme başarısız olursa 1 retry, sonra temiz bir
hata (HTML fallback şu an implement edilmedi - Sprint 3'te değerlendirilecek).
"""
import asyncio
import re
import tempfile
from pathlib import Path
from typing import Any, Optional

from app.exceptions import APIException, ValidationException
from app.logging_config import get_logger
from app.models import Document
from app.services.storage import StorageService, get_storage_service
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("cv_generation_agent")

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

_LATEX_SPECIAL_CHARS = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}
_LATEX_ESCAPE_RE = re.compile("|".join(re.escape(c) for c in _LATEX_SPECIAL_CHARS))


def latex_escape(value: Any) -> str:
    """Kullanıcı verisini (isim, özet vb.) LaTeX'e güvenle basar - injection/derleme
    hatası önler (ör. '#' veya '_' geçen bir isim CV'yi kırmasın)"""
    text = str(value or "")
    return _LATEX_ESCAPE_RE.sub(lambda m: _LATEX_SPECIAL_CHARS[m.group()], text)


_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    block_start_string=r"\BLOCK{",
    block_end_string="}",
    variable_start_string=r"\VAR{",
    variable_end_string="}",
    comment_start_string=r"\#{",
    comment_end_string="}",
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=False,
)
_jinja_env.filters["latex_escape"] = latex_escape


class CVGenerationException(APIException):
    def __init__(self, detail: str = "CV generation failed"):
        super().__init__(detail, status_code=503, error_code="CV_GENERATION_ERROR")


class CVGenerationAgent:
    def __init__(self, storage: Optional[StorageService] = None):
        self.storage = storage or get_storage_service()

    def _render_latex(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        matched_skills: list[str],
    ) -> str:
        skills = set(user_profile.get("skills") or [])
        matched = sorted(skills & set(matched_skills)) if matched_skills else []
        other = sorted(skills - set(matched))

        template = _jinja_env.get_template("cv_template.tex.jinja")
        return template.render(
            full_name=latex_escape(user_profile.get("full_name") or "Aday"),
            target_position=latex_escape(
                job_analysis.get("position_title") or user_profile.get("target_position") or ""
            ),
            email=latex_escape(user_profile.get("email") or ""),
            phone=latex_escape(user_profile.get("phone") or ""),
            experience_summary=latex_escape(
                user_profile.get("experience_summary") or "Deneyim özeti eklenmedi."
            ),
            matched_skills=[latex_escape(s) for s in matched],
            other_skills=[latex_escape(s) for s in other],
            experience_years=latex_escape(user_profile.get("experience_years") or "belirtilmemiş"),
            seniority=latex_escape(user_profile.get("seniority") or "belirtilmemiş"),
            target_company=latex_escape(job_analysis.get("company") or ""),
        )

    async def _compile_with_tectonic(self, tex_source: str, max_retries: int = 2) -> bytes:
        last_error = ""
        for attempt in range(1, max_retries + 1):
            with tempfile.TemporaryDirectory() as tmpdir:
                tex_path = Path(tmpdir) / "cv.tex"
                pdf_path = Path(tmpdir) / "cv.pdf"
                tex_path.write_text(tex_source, encoding="utf-8")

                proc = await asyncio.create_subprocess_exec(
                    "tectonic",
                    str(tex_path),
                    "--outdir",
                    tmpdir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                try:
                    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
                except asyncio.TimeoutError:
                    proc.kill()
                    last_error = "tectonic timed out after 60s"
                    logger.warning("cv_tectonic_timeout", attempt=attempt)
                    continue

                if proc.returncode == 0 and pdf_path.exists():
                    logger.info("cv_tectonic_success", attempt=attempt)
                    return pdf_path.read_bytes()

                last_error = stderr.decode(errors="replace")[-500:]
                logger.warning(
                    "cv_tectonic_failed",
                    attempt=attempt,
                    returncode=proc.returncode,
                    error=last_error,
                )

        raise CVGenerationException(
            f"LaTeX compilation failed after {max_retries} attempts: {last_error}"
        )

    async def generate(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        matched_skills: Optional[list[str]] = None,
    ) -> bytes:
        if not user_profile:
            raise ValidationException("user_profile zorunludur")

        tex_source = self._render_latex(user_profile, job_analysis or {}, matched_skills or [])
        return await self._compile_with_tectonic(tex_source)

    async def generate_and_save(
        self,
        db: AsyncSession,
        user_id: str,
        listing_id: Optional[str],
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        matched_skills: Optional[list[str]] = None,
    ) -> Document:
        pdf_bytes = await self.generate(user_profile, job_analysis, matched_skills)
        cv_url = self.storage.upload_cv(user_id, pdf_bytes)

        document = Document(user_id=user_id, listing_id=listing_id, doc_type="cv", cv_url=cv_url)
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document


_agent: Optional[CVGenerationAgent] = None


def get_cv_generation_agent() -> CVGenerationAgent:
    global _agent
    if _agent is None:
        _agent = CVGenerationAgent()
    return _agent
