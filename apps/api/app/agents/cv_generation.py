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
from app.observability import agent_run
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

_MAX_PROJECTS_ON_CV = 3


def _rank_projects(
    projects: list[dict[str, Any]], job_analysis: dict[str, Any], limit: int
) -> list[dict[str, Any]]:
    """Kullanıcının projelerini ilanın istediği tech stack'e göre sıralar.

    Aday birden fazla teknoloji setinde proje yapmış olabilir (ör. biri C#,
    biri Java, biri Python) - CV'de hepsini basmak yerine bu ilana en alakalı
    olanları öne çıkarır. Skor: proje tech_stack'inin, ilanın required +
    nice_to_have becerileriyle örtüşen beceri sayısı. Eşitlikte orijinal sıra
    korunur (stabil sort); hiç proje yoksa boş liste döner (opsiyonel bölüm).
    """
    if not projects:
        return []

    wanted = {
        s.strip().lower()
        for s in (job_analysis.get("required_skills") or [])
        + (job_analysis.get("nice_to_have_skills") or [])
        if s and s.strip()
    }

    def score(project: dict[str, Any]) -> int:
        stack = {str(t).strip().lower() for t in (project.get("tech_stack") or [])}
        return len(stack & wanted)

    ranked = sorted(enumerate(projects), key=lambda pair: (-score(pair[1]), pair[0]))
    return [project for _, project in ranked[:limit]]


def _sorted_experiences(experiences: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """En güncel iş deneyimi en üstte (end_date yok = hâlâ çalışıyor, en üstte)"""
    return sorted(
        experiences,
        key=lambda exp: exp.get("end_date") or "9999-99-99",
        reverse=True,
    )


def _format_period(experience: dict[str, Any]) -> str:
    start = experience.get("start_date") or "?"
    end = experience.get("end_date") or "halen"
    return f"{start} - {end}"


class CVGenerationException(APIException):
    def __init__(self, detail: str = "CV oluşturulamadı"):
        super().__init__(detail, status_code=422, error_code="CV_GENERATION_ERROR")


class CVGenerationAgent:
    def __init__(self, storage: Optional[StorageService] = None):
        self.storage = storage or get_storage_service()

    def _render_latex(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
    ) -> str:
        skills = sorted(set(user_profile.get("skills") or []))
        relevant_projects = _rank_projects(
            user_profile.get("projects") or [], job_analysis, limit=_MAX_PROJECTS_ON_CV
        )
        experiences = _sorted_experiences(user_profile.get("work_experiences") or [])

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
            all_skills=[latex_escape(s) for s in skills],
            experience_years=latex_escape(user_profile.get("experience_years") or "belirtilmemiş"),
            seniority=latex_escape(user_profile.get("seniority") or "belirtilmemiş"),
            work_experiences=[
                {
                    "company": latex_escape(exp.get("company")),
                    "title": latex_escape(exp.get("title")),
                    "period": latex_escape(_format_period(exp)),
                    "description": latex_escape(exp.get("description")),
                }
                for exp in experiences
            ],
            projects=[
                {
                    "title": latex_escape(proj.get("title")),
                    "description": latex_escape(proj.get("description")),
                    "tech_stack": ", ".join(
                        latex_escape(t) for t in (proj.get("tech_stack") or [])
                    ),
                }
                for proj in relevant_projects
            ],
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

        logger.error("cv_tectonic_exhausted", attempts=max_retries, error=last_error)
        raise CVGenerationException(
            "CV PDF oluşturulamadı: LaTeX derlemesi başarısız oldu. "
            "Lütfen daha sonra tekrar deneyin."
        )

    async def generate(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
    ) -> bytes:
        if not user_profile:
            raise ValidationException("user_profile zorunludur")

        async with agent_run(
            "cv_generation",
            position=(job_analysis or {}).get("position_title"),
        ):
            tex_source = self._render_latex(user_profile, job_analysis or {})
            pdf_bytes = await self._compile_with_tectonic(tex_source)
            if not pdf_bytes or not pdf_bytes.startswith(b"%PDF"):
                raise CVGenerationException("Üretilen dosya geçerli bir PDF değil")
            return pdf_bytes

    async def generate_and_save(
        self,
        db: AsyncSession,
        user_id: str,
        listing_id: Optional[str],
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
    ) -> Document:
        pdf_bytes = await self.generate(user_profile, job_analysis)
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
