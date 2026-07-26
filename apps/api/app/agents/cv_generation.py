"""CV Ajanı: profil + ilan eşleştirmesi -> derlenmiş LaTeX PDF CV.

En riskli adım (Tectonic Docker'da çalışıyor mu) - `apps/api/Dockerfile`'da amd64
emülasyonu + debian:trixie-slim ile çözüldü (Apple Silicon'da arm64 Tectonic binary'si
yok, glibc uyumsuzluğu vardı). Derleme başarısız olursa 1 retry, sonra temiz bir
hata (HTML fallback şu an implement edilmedi - Sprint 3'te değerlendirilecek).
"""
import asyncio
import json
import re
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

from app.agents.prompt_safety import build_cv_content_edit_section, build_extra_prompt_section
from app.agents.strategy import select_strategy
from app.exceptions import APIException, GeminiAPIException, ValidationException
from app.logging_config import get_logger
from app.models import Document
from app.observability import agent_run
from app.services.gemini_client import GeminiClient, get_gemini_client, render_prompt
from app.services.storage import StorageService, get_storage_service
from jinja2 import Environment, FileSystemLoader
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("cv_generation_agent")

# CV özeti LLM çıktısı panoya değil PDF'e gidiyor ama yine de markdown eklerse temizler
_MARKDOWN_ARTIFACTS = re.compile(r"[*_#`]+")

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

CV_TEMPLATE_IDS = (
    "Version1",
    "Version2",
    "Version3",
    "Version4",
    "Version5",
)
DEFAULT_CV_TEMPLATE = "Version1"
_LEGACY_CV_TEMPLATE_MAP = {
    "1": "Version1",
    "2": "Version2",
    "3": "Version3",
    "4": "Version4",
    "5": "Version5",
    "6": "Version5",
    # Eski 6'lı katalog: silinen/kaydırılan id'ler
    "Version6": "Version5",
}


def normalize_cv_template_id(cv_template: Optional[str]) -> str:
    """İlan cv_template değerini VersionN allowlist'ine çeker; bilinmeyen → Version1."""
    if not cv_template or not str(cv_template).strip():
        return DEFAULT_CV_TEMPLATE
    trimmed = str(cv_template).strip()
    if trimmed in CV_TEMPLATE_IDS:
        return trimmed
    return _LEGACY_CV_TEMPLATE_MAP.get(trimmed, DEFAULT_CV_TEMPLATE)


# generate_json'a verilen response_schema - google-generativeai SDK OpenAPI benzeri
# tip adları bekler (büyük harf "OBJECT"/"ARRAY"/"INTEGER").
_REWRITE_ITEM_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {"index": {"type": "INTEGER"}, "description": {"type": "STRING"}},
    "required": ["index", "description"],
}

CV_CONTENT_FILTER_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "experience_indices": {"type": "ARRAY", "items": {"type": "INTEGER"}},
        "project_indices": {"type": "ARRAY", "items": {"type": "INTEGER"}},
        "certificate_indices": {"type": "ARRAY", "items": {"type": "INTEGER"}},
        "experience_rewrites": {"type": "ARRAY", "items": _REWRITE_ITEM_SCHEMA},
        "project_rewrites": {"type": "ARRAY", "items": _REWRITE_ITEM_SCHEMA},
    },
    "required": ["experience_indices", "project_indices", "certificate_indices"],
}

CV_SHORTEN_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "experience_rewrites": {"type": "ARRAY", "items": _REWRITE_ITEM_SCHEMA},
        "project_rewrites": {"type": "ARRAY", "items": _REWRITE_ITEM_SCHEMA},
    },
    "required": ["experience_rewrites", "project_rewrites"],
}


def _describe_experiences(experiences: list[dict[str, Any]]) -> str:
    lines = [
        f"{i}: {exp.get('title') or ''} - {exp.get('company') or ''} "
        f"| {exp.get('description') or ''}"
        for i, exp in enumerate(experiences)
    ]
    return "\n".join(lines) or "(yok)"


def _describe_projects(projects: list[dict[str, Any]]) -> str:
    lines = [
        f"{i}: {p.get('title') or ''} [{', '.join(p.get('tech_stack') or [])}] "
        f"| {p.get('description') or ''}"
        for i, p in enumerate(projects)
    ]
    return "\n".join(lines) or "(yok)"


def _describe_certificates(certificates: list[dict[str, Any]]) -> str:
    lines = [
        f"{i}: {c.get('title') or ''} - {c.get('issuer') or ''}" for i, c in enumerate(certificates)
    ]
    return "\n".join(lines) or "(yok)"


def _select_indices(items: list[dict[str, Any]], indices: list[int]) -> list[dict[str, Any]]:
    """LLM'in seçtiği index'lere göre alt küme döner. Seçim boşsa veya tamamen
    geçersizse (LLM hatalı/boş döndürdüyse) hepsini gösterir - bir öğeyi yanlışlıkla
    CV'den tamamen düşürmek, alakasız bir öğeyi göstermekten daha kötü bir hata."""
    if not items:
        return []
    valid = {i for i in indices if isinstance(i, int) and 0 <= i < len(items)}
    if not valid:
        return items
    return [item for i, item in enumerate(items) if i in valid]


_MAX_DESCRIPTION_CHARS = 280


def _clamp_description(text: Any) -> str:
    """Deneyim/proje açıklamasını ~1–2 cümle / 280 karaktere indirger."""
    if text is None:
        return ""
    value = str(text).strip()
    if len(value) <= _MAX_DESCRIPTION_CHARS:
        return value
    truncated = value[:_MAX_DESCRIPTION_CHARS]
    for sep in (". ", "! ", "? ", ".\n", "!\n", "?\n"):
        idx = truncated.rfind(sep)
        if idx >= 60:
            return truncated[: idx + 1].strip()
    space = truncated.rfind(" ")
    if space >= 60:
        return truncated[:space].rstrip() + "…"
    return truncated.rstrip() + "…"


def _select_and_rewrite(
    items: list[dict[str, Any]], indices: list[int], rewrites: dict[int, str]
) -> list[dict[str, Any]]:
    """_select_indices ile aynı fail-open seçim mantığı; ek olarak seçilen öğelerin
    description alanını (varsa) ilana göre yeniden yazılmış/kısaltılmış metinle
    değiştirir. Rewrite verilmemiş bir öğe orijinal metniyle kalır (fail-open).
    Her durumda açıklama uzunluk tavanına (`_clamp_description`) çekilir."""
    if not items:
        return []
    valid = {i for i in indices if isinstance(i, int) and 0 <= i < len(items)}
    chosen = valid if valid else set(range(len(items)))
    result = []
    for i, item in enumerate(items):
        if i not in chosen:
            continue
        rewritten = rewrites.get(i)
        raw = rewritten if rewritten else item.get("description")
        clamped = _clamp_description(raw) if raw else ""
        if clamped != (item.get("description") or ""):
            result.append({**item, "description": clamped})
        else:
            result.append(item)
    return result


def _languages_line(languages: list[dict[str, Any]]) -> str:
    """Örn. 'İngilizce (İleri) | Almanca (Orta)' — LaTeX-escaped."""
    parts: list[str] = []
    for lang in languages or []:
        name = latex_escape(lang.get("name") or "")
        level = latex_escape(lang.get("level") or "")
        if name and level:
            parts.append(f"{name} ({level})")
        elif name:
            parts.append(name)
    return " | ".join(parts)


def _avatar_filename(image_bytes: bytes) -> str:
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "avatar.png"
    if image_bytes[:4] == b"RIFF" and len(image_bytes) >= 12 and image_bytes[8:12] == b"WEBP":
        return "avatar.webp"
    return "avatar.jpg"


def _rewrites_to_map(rewrite_items: list[dict[str, Any]]) -> dict[int, str]:
    """generate_json'dan gelen [{index, description}, ...] listesini index->metin
    sözlüğüne çevirir; geçersiz/eksik girişleri sessizce atar."""
    return {
        item["index"]: item["description"]
        for item in rewrite_items or []
        if isinstance(item, dict) and isinstance(item.get("index"), int) and item.get("description")
    }


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


_TR_MONTHS = (
    "",
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
)


def _format_month_year(value: Any) -> str:
    """YYYY-MM(-DD) veya date → 'Haziran 2024' (yalnızca ay metni + yıl)."""
    if value is None or value == "":
        return ""
    if hasattr(value, "year") and hasattr(value, "month"):
        year, month = int(value.year), int(value.month)
    else:
        text = str(value).strip()
        # ISO: 2024-06-01 / 2024-06
        match = re.match(r"^(\d{4})-(\d{1,2})", text)
        if not match:
            return text
        year, month = int(match.group(1)), int(match.group(2))
    if not 1 <= month <= 12:
        return str(value)
    return f"{_TR_MONTHS[month]} {year}"


def _format_period(item: dict[str, Any]) -> str:
    start = _format_month_year(item.get("start_date"))
    if item.get("end_date"):
        end = _format_month_year(item.get("end_date"))
    else:
        end = "devam ediyor" if start else ""
    if start and end:
        return f"{start} - {end}"
    return start or end or "?"


def _sorted_education(education: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """En güncel eğitim en üstte (end_date yok = hâlâ devam ediyor, en üstte)"""
    return sorted(
        education,
        key=lambda edu: edu.get("end_date") or "9999-99-99",
        reverse=True,
    )


def _pdf_page_count(pdf_bytes: bytes) -> int:
    """PDF sayfa sayısını döner; okunamazsa 0 (US-015: en az 1 sayfa doğrulaması)"""
    try:
        return len(PdfReader(BytesIO(pdf_bytes)).pages)
    except PdfReadError:
        return 0


class CVGenerationException(APIException):
    def __init__(self, detail: str = "CV oluşturulamadı"):
        super().__init__(detail, status_code=422, error_code="CV_GENERATION_ERROR")


class CVGenerationAgent:
    def __init__(
        self,
        storage: Optional[StorageService] = None,
        client: Optional[GeminiClient] = None,
    ):
        self.storage = storage or get_storage_service()
        self._client = client

    @property
    def client(self) -> GeminiClient:
        """Lazy: extra_prompt verilmediği sürece Gemini'ye hiç ihtiyaç duyulmaz -
        CV üretiminin varsayılan (LLM'siz, deterministik) yolu kotayı tüketmemeli."""
        if self._client is None:
            self._client = get_gemini_client()
        return self._client

    async def _generate_ai_summary(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        matching_gaps: dict[str, Any],
        extra_prompt: str,
    ) -> str:
        """US-050: extra_prompt verildiğinde 'Özet' bölümünü Gemini ile, ekstra
        vurgu notunu ve düşük-skor stratejisini dikkate alarak yeniden yazdırır."""
        strategy = select_strategy(matching_gaps)
        prompt = render_prompt(
            "cv_summary",
            user_profile=json.dumps(user_profile, ensure_ascii=False),
            job_analysis=json.dumps(job_analysis, ensure_ascii=False),
            matching_gaps=json.dumps(matching_gaps, ensure_ascii=False),
            strategy=strategy,
            extra_prompt_section=build_extra_prompt_section(extra_prompt),
        )
        raw_text = await self.client.generate_text(prompt, temperature=0.7)
        return _MARKDOWN_ARTIFACTS.sub("", raw_text).strip()

    @staticmethod
    def _has_filterable_content(user_profile: dict[str, Any]) -> bool:
        return bool(
            user_profile.get("work_experiences")
            or user_profile.get("projects")
            or user_profile.get("certificates")
        )

    async def _select_relevant_content(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        extra_prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        """Profildeki deneyim/proje/sertifikayı seçer ve kısaltır/yeniden yazar.

        Varsayılan: ilanla alakalı olanlar. extra_prompt varsa kullanıcı
        ekleme/çıkarma/kısaltma/yeniden yazma istekleri önceliklidir."""
        prompt = render_prompt(
            "cv_content_filter",
            experiences=_describe_experiences(user_profile.get("work_experiences") or []),
            projects=_describe_projects(user_profile.get("projects") or []),
            certificates=_describe_certificates(user_profile.get("certificates") or []),
            position_title=job_analysis.get("position_title") or "belirtilmemiş",
            required_skills=", ".join(job_analysis.get("required_skills") or []) or "belirtilmemiş",
            nice_to_have_skills=", ".join(job_analysis.get("nice_to_have_skills") or []) or "yok",
            extra_prompt_section=build_cv_content_edit_section(extra_prompt),
        )
        result = await self.client.generate_json(prompt, response_schema=CV_CONTENT_FILTER_SCHEMA)
        exp_rewrites = {
            i: _clamp_description(text)
            for i, text in _rewrites_to_map(result.get("experience_rewrites") or []).items()
        }
        proj_rewrites = {
            i: _clamp_description(text)
            for i, text in _rewrites_to_map(result.get("project_rewrites") or []).items()
        }
        return {
            "experience_indices": result.get("experience_indices") or [],
            "project_indices": result.get("project_indices") or [],
            "certificate_indices": result.get("certificate_indices") or [],
            "experience_rewrites": exp_rewrites,
            "project_rewrites": proj_rewrites,
        }

    async def _shorten_overflowing_content(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        content_selection: dict[str, Any],
        extra_prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        """CV 1 sayfayı aştığında, halihazırda CV'ye dahil edilmiş (ve varsa daha önce
        ilana göre yeniden yazılmış) deneyim/proje açıklamalarını anlam kaybı olmadan
        kısaltmak için ek bir LLM adımı. Sadece dahil edilen alt küme gönderilir -
        çıkarılmış olan öğeler zaten CV'de yer almadığı için kısaltmaya gerek yok."""
        experiences = user_profile.get("work_experiences") or []
        projects = user_profile.get("projects") or []
        exp_indices = content_selection.get("experience_indices") or list(range(len(experiences)))
        proj_indices = content_selection.get("project_indices") or list(range(len(projects)))
        exp_rewrites = content_selection.get("experience_rewrites") or {}
        proj_rewrites = content_selection.get("project_rewrites") or {}

        current_experiences = [
            {
                **experiences[i],
                "description": exp_rewrites.get(i, experiences[i].get("description")),
            }
            for i in exp_indices
            if 0 <= i < len(experiences)
        ]
        current_projects = [
            {
                **projects[i],
                "description": proj_rewrites.get(i, projects[i].get("description")),
            }
            for i in proj_indices
            if 0 <= i < len(projects)
        ]

        prompt = render_prompt(
            "cv_shorten_content",
            experiences=_describe_experiences(current_experiences),
            projects=_describe_projects(current_projects),
            position_title=job_analysis.get("position_title") or "belirtilmemiş",
            required_skills=", ".join(job_analysis.get("required_skills") or []) or "belirtilmemiş",
            nice_to_have_skills=", ".join(job_analysis.get("nice_to_have_skills") or []) or "yok",
            extra_prompt_section=build_cv_content_edit_section(extra_prompt),
        )
        result = await self.client.generate_json(prompt, response_schema=CV_SHORTEN_SCHEMA)

        new_exp_rewrites = dict(exp_rewrites)
        for local_i, description in _rewrites_to_map(
            result.get("experience_rewrites") or []
        ).items():
            if 0 <= local_i < len(exp_indices):
                new_exp_rewrites[exp_indices[local_i]] = _clamp_description(description)

        new_proj_rewrites = dict(proj_rewrites)
        for local_i, description in _rewrites_to_map(result.get("project_rewrites") or []).items():
            if 0 <= local_i < len(proj_indices):
                new_proj_rewrites[proj_indices[local_i]] = _clamp_description(description)

        return {
            **content_selection,
            "experience_indices": exp_indices,
            "project_indices": proj_indices,
            "experience_rewrites": new_exp_rewrites,
            "project_rewrites": new_proj_rewrites,
        }

    def _load_avatar_bytes(self, user_profile: dict[str, Any]) -> Optional[bytes]:
        url = user_profile.get("avatar_url")
        if not url:
            logger.info("cv_avatar_missing", reason="no_avatar_url")
            return None
        try:
            data = self.storage.download_bytes(str(url))
            if not data:
                logger.warning("cv_avatar_download_empty", url=str(url)[:120])
            return data
        except Exception as exc:  # noqa: BLE001 — foto yoksa placeholder'a düş
            logger.warning("cv_avatar_download_failed", error=str(exc))
            return None

    async def _recompile_with_selection(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        ai_summary: Optional[str],
        content_selection: dict[str, Any],
        cv_template: str = DEFAULT_CV_TEMPLATE,
        avatar_bytes: Optional[bytes] = None,
    ) -> Optional[bytes]:
        """Seçimle yeniden derler; başarısızsa None döner (fail-open için)."""
        tex_source = self._render_latex(
            user_profile,
            job_analysis,
            ai_summary,
            content_selection,
            cv_template=cv_template,
            has_photo=bool(avatar_bytes),
            avatar_filename=_avatar_filename(avatar_bytes) if avatar_bytes else "avatar.jpg",
        )
        try:
            pdf_bytes = await self._compile_with_tectonic(tex_source, avatar_bytes=avatar_bytes)
        except CVGenerationException as exc:
            logger.warning("cv_overflow_recompile_failed", error=str(exc))
            return None
        if pdf_bytes and pdf_bytes.startswith(b"%PDF") and _pdf_page_count(pdf_bytes) >= 1:
            return pdf_bytes
        return None

    async def _try_fit_to_one_page(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        ai_summary: Optional[str],
        content_selection: Optional[dict[str, Any]],
        original_pdf: bytes,
        cv_template: str = DEFAULT_CV_TEMPLATE,
        avatar_bytes: Optional[bytes] = None,
        extra_prompt: Optional[str] = None,
    ) -> bytes:
        """CV 1 sayfayı aşarsa önce paragrafları ilana göre kısaltır, hâlâ >1 sayfa
        ise en az alakalı projeleri tek tek düşürür. Her adım fail-open: LLM/derleme
        hatasında mevcut en iyi PDF korunur; üretim asla kırılmaz."""
        selection = dict(content_selection or {})
        experiences = user_profile.get("work_experiences") or []
        projects = user_profile.get("projects") or []
        exp_indices = selection.get("experience_indices") or list(range(len(experiences)))
        proj_indices = selection.get("project_indices") or list(range(len(projects)))
        best_pdf = original_pdf
        best_pages = _pdf_page_count(original_pdf)
        template_id = normalize_cv_template_id(cv_template)

        if exp_indices or proj_indices:
            try:
                selection = await self._shorten_overflowing_content(
                    user_profile, job_analysis, selection, extra_prompt=extra_prompt
                )
                shortened_pdf = await self._recompile_with_selection(
                    user_profile,
                    job_analysis,
                    ai_summary,
                    selection,
                    cv_template=template_id,
                    avatar_bytes=avatar_bytes,
                )
            except GeminiAPIException as exc:
                logger.warning("cv_shorten_failed", error=str(exc))
                shortened_pdf = None

            if shortened_pdf:
                pages = _pdf_page_count(shortened_pdf)
                logger.info(
                    "cv_shortened_for_overflow",
                    pages_before=best_pages,
                    pages_after=pages,
                )
                if pages <= best_pages:
                    best_pdf, best_pages = shortened_pdf, pages
                if best_pages <= 1:
                    return best_pdf

        # Paragraf kısaltması yetmezse (veya hiç denenemediyse): proje kotasını düşür.
        max_projects = int(selection.get("max_projects") or _MAX_PROJECTS_ON_CV)
        while best_pages > 1 and max_projects > 0:
            max_projects -= 1
            selection = {**selection, "max_projects": max_projects}
            pruned_pdf = await self._recompile_with_selection(
                user_profile,
                job_analysis,
                ai_summary,
                selection,
                cv_template=template_id,
                avatar_bytes=avatar_bytes,
            )
            if not pruned_pdf:
                break
            pages = _pdf_page_count(pruned_pdf)
            logger.info(
                "cv_pruned_project_for_overflow",
                max_projects=max_projects,
                pages_before=best_pages,
                pages_after=pages,
            )
            if pages <= best_pages:
                best_pdf, best_pages = pruned_pdf, pages
            if best_pages <= 1:
                return best_pdf

        return best_pdf

    def _render_latex(
        self,
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        ai_summary: Optional[str] = None,
        content_selection: Optional[dict[str, Any]] = None,
        cv_template: Optional[str] = None,
        has_photo: bool = False,
        avatar_filename: str = "avatar.jpg",
    ) -> str:
        skills = sorted(set(user_profile.get("skills") or []))
        selection = content_selection or {}
        filtered_projects = _select_and_rewrite(
            user_profile.get("projects") or [],
            selection.get("project_indices") or [],
            selection.get("project_rewrites") or {},
        )
        filtered_experiences = _select_and_rewrite(
            user_profile.get("work_experiences") or [],
            selection.get("experience_indices") or [],
            selection.get("experience_rewrites") or {},
        )
        filtered_certificates = _select_indices(
            user_profile.get("certificates") or [],
            selection.get("certificate_indices") or [],
        )
        project_limit = selection.get("max_projects", _MAX_PROJECTS_ON_CV)
        try:
            project_limit = max(0, int(project_limit))
        except (TypeError, ValueError):
            project_limit = _MAX_PROJECTS_ON_CV
        relevant_projects = _rank_projects(filtered_projects, job_analysis, limit=project_limit)
        experiences = _sorted_experiences(filtered_experiences)
        education = _sorted_education(user_profile.get("education") or [])
        languages_line = _languages_line(user_profile.get("languages") or [])

        # Kişisel bilgiler - TR CV geleneği (yalnızca doldurulmuşsa gösterilir)
        personal_info = [
            (label, latex_escape(value))
            for label, value in (
                ("Cinsiyet", user_profile.get("gender")),
                ("Uyruk", user_profile.get("nationality")),
                ("Doğum Yılı", user_profile.get("birth_year")),
                ("Askerlik Durumu", user_profile.get("military_status")),
                ("Sürücü Belgesi", user_profile.get("driver_license")),
            )
            if value
        ]

        template_id = normalize_cv_template_id(cv_template)
        template = _jinja_env.get_template(f"cv/{template_id}.tex.jinja")
        summary_raw = ai_summary or user_profile.get("experience_summary") or ""
        return template.render(
            full_name=latex_escape(user_profile.get("full_name") or "Aday"),
            target_position=latex_escape(
                job_analysis.get("position_title") or user_profile.get("target_position") or ""
            ),
            email=latex_escape(user_profile.get("email") or ""),
            phone=latex_escape(user_profile.get("phone") or ""),
            experience_summary=latex_escape(summary_raw),
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
            education=[
                {
                    "school": latex_escape(edu.get("school")),
                    "degree": latex_escape(edu.get("degree")),
                    "field_of_study": latex_escape(edu.get("field_of_study")),
                    "period": latex_escape(_format_period(edu)),
                    "description": latex_escape(edu.get("description")),
                }
                for edu in education
            ],
            personal_info=personal_info,
            location=latex_escape(user_profile.get("location") or ""),
            certificates=[
                {
                    "title": latex_escape(cert.get("title")),
                    "issuer": latex_escape(cert.get("issuer")),
                    "issue_date": latex_escape(_format_month_year(cert.get("issue_date"))),
                }
                for cert in filtered_certificates
            ],
            languages=[
                {
                    "name": latex_escape(lang.get("name")),
                    "level": latex_escape(lang.get("level")),
                }
                for lang in (user_profile.get("languages") or [])
            ],
            languages_line=languages_line,
            has_photo=has_photo,
            avatar_filename=avatar_filename,
            social_links=[
                {
                    "platform": latex_escape(link.get("platform")),
                    # href URL'lerinde LaTeX escape URL'yi bozar
                    "url": str(link.get("url") or ""),
                }
                for link in (user_profile.get("social_links") or [])
            ],
            references=[
                {
                    "name": latex_escape(ref.get("name")),
                    "title": latex_escape(ref.get("title")),
                    "company": latex_escape(ref.get("company")),
                    "contact": latex_escape(ref.get("contact")),
                }
                for ref in (user_profile.get("references") or [])
            ],
            exams=[
                {
                    "name": latex_escape(exam.get("name")),
                    "score": latex_escape(exam.get("score")),
                    "exam_date": latex_escape(_format_month_year(exam.get("exam_date"))),
                    "description": latex_escape(exam.get("description")),
                }
                for exam in (user_profile.get("exams") or [])
            ],
        )

    async def _compile_with_tectonic(
        self,
        tex_source: str,
        max_retries: int = 2,
        avatar_bytes: Optional[bytes] = None,
    ) -> bytes:
        last_error = ""
        for attempt in range(1, max_retries + 1):
            with tempfile.TemporaryDirectory() as tmpdir:
                tex_path = Path(tmpdir) / "cv.tex"
                pdf_path = Path(tmpdir) / "cv.pdf"
                tex_path.write_text(tex_source, encoding="utf-8")
                if avatar_bytes:
                    (Path(tmpdir) / _avatar_filename(avatar_bytes)).write_bytes(avatar_bytes)

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
        matching_gaps: Optional[dict[str, Any]] = None,
        extra_prompt: Optional[str] = None,
        cv_template: Optional[str] = None,
    ) -> bytes:
        if not user_profile:
            raise ValidationException("user_profile zorunludur")

        template_id = normalize_cv_template_id(
            cv_template or (job_analysis or {}).get("cv_template")
        )

        async with agent_run(
            "cv_generation",
            position=(job_analysis or {}).get("position_title"),
        ):
            ai_summary = None
            if extra_prompt:
                # US-050: ekstra prompt verilmişse Özet bölümü Gemini ile yeniden
                # yazılır; LLM çağrısı başarısız olursa CV üretimini bozmadan
                # profildeki mevcut özete sessizce geri dönülür.
                try:
                    ai_summary = await self._generate_ai_summary(
                        user_profile,
                        job_analysis or {},
                        matching_gaps or {},
                        extra_prompt,
                    )
                except GeminiAPIException as exc:
                    logger.warning("cv_ai_summary_failed", error=str(exc))

            content_selection = None
            if self._has_filterable_content(user_profile):
                # Varsayılan: ilanla alakalı içerik. extra_prompt ile kullanıcı
                # ekleme/çıkarma/kısaltma isteyebilir. LLM fail → tüm içerik (fail-open).
                try:
                    content_selection = await self._select_relevant_content(
                        user_profile, job_analysis or {}, extra_prompt=extra_prompt
                    )
                except GeminiAPIException as exc:
                    logger.warning("cv_content_filter_failed", error=str(exc))

            avatar_bytes = self._load_avatar_bytes(user_profile)
            avatar_name = _avatar_filename(avatar_bytes) if avatar_bytes else "avatar.jpg"
            tex_source = self._render_latex(
                user_profile,
                job_analysis or {},
                ai_summary,
                content_selection,
                cv_template=template_id,
                has_photo=bool(avatar_bytes),
                avatar_filename=avatar_name,
            )
            pdf_bytes = await self._compile_with_tectonic(tex_source, avatar_bytes=avatar_bytes)
            if not pdf_bytes or not pdf_bytes.startswith(b"%PDF"):
                raise CVGenerationException("Üretilen dosya geçerli bir PDF değil")
            page_count = _pdf_page_count(pdf_bytes)
            if page_count < 1:
                raise CVGenerationException("Üretilen PDF en az 1 sayfa içermeli")

            if page_count > 1:
                # 1) paragrafları kısalt 2) yetmezse en az alakalı projeleri düşür.
                pdf_bytes = await self._try_fit_to_one_page(
                    user_profile,
                    job_analysis or {},
                    ai_summary,
                    content_selection,
                    pdf_bytes,
                    cv_template=template_id,
                    avatar_bytes=avatar_bytes,
                    extra_prompt=extra_prompt,
                )
            return pdf_bytes

    async def generate_and_save(
        self,
        db: AsyncSession,
        user_id: str,
        listing_id: Optional[str],
        user_profile: dict[str, Any],
        job_analysis: dict[str, Any],
        matching_gaps: Optional[dict[str, Any]] = None,
        extra_prompt: Optional[str] = None,
        cv_template: Optional[str] = None,
    ) -> Document:
        pdf_bytes = await self.generate(
            user_profile,
            job_analysis,
            matching_gaps=matching_gaps,
            extra_prompt=extra_prompt,
            cv_template=cv_template or (job_analysis or {}).get("cv_template"),
        )
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
