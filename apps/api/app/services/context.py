"""Context Manager: Agent'lar için merkezi veri yükleyici (US-017)

Agent'lar şu an dict payload alıyor; DB'den profil, ilan, match, deneyim ve projeleri
tek yerden yükleyen context katmanı gerekir.

Thread-safe / async-safe; JSON serializable.
"""
import json
from typing import Any

from app.logging_config import get_logger
from app.models import EducationRecord, JobListing, Match, Project, User, WorkExperience
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("context_manager")


def _parse_json(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _listing_skills(listing: JobListing, parsed: dict[str, Any], key: str) -> list[str]:
    column_value = getattr(listing, key, None)
    if column_value:
        return _parse_json(column_value, [])
    skills = parsed.get(key)
    return skills if isinstance(skills, list) else []


def job_analysis_from_context(context: dict[str, Any]) -> dict[str, Any]:
    """Agent'lar için ilan analizi: parsed_json + kolon fallback."""
    listing = context["listing"]
    parsed = listing.get("parsed_json") or {}
    if not isinstance(parsed, dict):
        parsed = {}

    analysis = dict(parsed)
    for key in ("required_skills", "nice_to_have_skills", "seniority"):
        if not analysis.get(key) and listing.get(key):
            analysis[key] = listing[key]
    if not analysis.get("position_title") and listing.get("title"):
        analysis["position_title"] = listing["title"]
    return analysis


def user_profile_for_agents(context: dict[str, Any]) -> dict[str, Any]:
    """CV / önyazı ajanları için kullanıcı profili.

    work_experiences, projects ve education de dahil - CV ajanı bunları bölüm
    olarak basar, projects ayrıca ilana göre en alakalı olacak şekilde CV
    ajanı tarafından sıralanıp kısaltılır (bkz. cv_generation._rank_projects).
    gender/nationality/driver_license/military_status "Kişisel Bilgiler"
    bölümünde basılır (TR CV geleneği - yalnızca doldurulmuşsa gösterilir)."""
    user = context["user"]
    return {
        "full_name": user.get("full_name"),
        "email": user.get("email"),
        "target_position": user.get("target_position"),
        "seniority": user.get("seniority"),
        "experience_years": user.get("experience_years"),
        "skills": user.get("skills") or [],
        "experience_summary": user.get("experience_summary"),
        "phone": user.get("phone"),
        "location": user.get("location"),
        "tone_preference": user.get("tone_preference"),
        "work_experiences": context.get("experiences") or [],
        "projects": context.get("projects") or [],
        "education": context.get("education") or [],
        "birth_year": user.get("birth_year"),
        "gender": user.get("gender"),
        "nationality": user.get("nationality"),
        "driver_license": user.get("driver_license"),
        "military_status": user.get("military_status"),
    }


def user_profile_for_matching(context: dict[str, Any]) -> dict[str, Any]:
    """Eşleştirme ajanı için profil + deneyim + proje."""
    user = context["user"]
    return {
        "skills": user.get("skills") or [],
        "seniority": user.get("seniority"),
        "work_experiences": [
            {
                "company": exp["company"],
                "title": exp["title"],
                "description": exp.get("description"),
            }
            for exp in context.get("experiences") or []
        ],
        "projects": [
            {
                "title": proj["title"],
                "description": proj.get("description"),
                "tech_stack": proj.get("tech_stack") or [],
            }
            for proj in context.get("projects") or []
        ],
    }


def matching_gaps_from_context(context: dict[str, Any]) -> dict[str, Any]:
    """Önyazı ajanı için eşleştirme eksikleri (match varsa)."""
    match = context.get("match")
    if not match:
        return {}
    return {
        "missing_skills": match.get("missing_skills") or [],
        "matched_skills": match.get("matched_skills") or [],
        "score": match.get("score"),
        "score_breakdown": match.get("score_breakdown"),
    }


class ContextManager:
    """Agent'lar için merkezi context yükleyici"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def load(self, user_id: str, listing_id: str) -> dict[str, Any]:
        """User ve listing ID'lerine göre tam context yükler

        Args:
            user_id: Kullanıcı ID
            listing_id: İlan ID

        Returns:
            Context dict: {
                "user": {user profil verileri},
                "listing": {ilan verileri},
                "match": {eşleştirme verileri, varsa},
                "experiences": [{iş deneyimleri}],
                "projects": [{projeler}]
            }
        """
        # User profilini yükle
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # Listing'i yükle
        listing_result = await self.db.execute(
            select(JobListing).where(JobListing.id == listing_id)
        )
        listing = listing_result.scalar_one_or_none()
        if not listing:
            raise ValueError(f"Listing not found: {listing_id}")

        # Match verisini yükle (varsa)
        match_result = await self.db.execute(
            select(Match).where(Match.user_id == user_id, Match.listing_id == listing_id)
        )
        match = match_result.scalar_one_or_none()

        # Work experiences'i yükle
        experiences_result = await self.db.execute(
            select(WorkExperience).where(WorkExperience.user_id == user_id)
        )
        experiences = experiences_result.scalars().all()

        # Projects'i yükle
        projects_result = await self.db.execute(select(Project).where(Project.user_id == user_id))
        projects = projects_result.scalars().all()

        # Eğitim kayıtlarını yükle
        education_result = await self.db.execute(
            select(EducationRecord)
            .where(EducationRecord.user_id == user_id)
            .order_by(EducationRecord.start_date.desc().nullslast())
        )
        education_records = education_result.scalars().all()

        # Context'i oluştur
        parsed_json = _parse_json(listing.parsed_json, {})
        if not isinstance(parsed_json, dict):
            parsed_json = {}

        context: dict[str, Any] = {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "target_position": user.target_position,
                "seniority": user.seniority,
                "experience_years": user.experience_years,
                "skills": _parse_json(user.skills, []),
                "experience_summary": user.experience_summary,
                "phone": user.phone,
                "location": user.location,
                "birth_year": user.birth_year,
                "tone_preference": user.tone_preference,
                "gender": user.gender,
                "nationality": user.nationality,
                "driver_license": user.driver_license,
                "military_status": user.military_status,
            },
            "listing": {
                "id": listing.id,
                "title": listing.title,
                "company": listing.company,
                "raw_text": listing.raw_text,
                "required_skills": _listing_skills(listing, parsed_json, "required_skills"),
                "nice_to_have_skills": _listing_skills(listing, parsed_json, "nice_to_have_skills"),
                "seniority": listing.seniority or parsed_json.get("seniority"),
                "parsed_json": parsed_json,
                "location": listing.location,
                "employment_type": listing.employment_type,
                "company_about": listing.company_about,
                "extra_notes": listing.extra_notes,
                "benefits": _parse_json(listing.benefits, []),
                "experience_level": listing.experience_level,
                "education_level": listing.education_level,
                "languages": _parse_json(listing.languages, []),
                "driver_license": listing.driver_license,
                "application_stage": listing.application_stage,
            },
            "match": None,
            "experiences": [],
            "projects": [],
            "education": [],
        }

        # Match varsa ekle
        if match:
            context["match"] = {
                "id": match.id,
                "score": match.score,
                "matched_skills": _parse_json(match.matched_skills, []),
                "missing_skills": _parse_json(match.missing_skills, []),
                "score_breakdown": _parse_json(match.score_breakdown, None),
            }

        # Experiences'ları ekle
        for exp in experiences:
            context["experiences"].append(
                {
                    "id": exp.id,
                    "company": exp.company,
                    "title": exp.title,
                    "start_date": exp.start_date.isoformat() if exp.start_date else None,
                    "end_date": exp.end_date.isoformat() if exp.end_date else None,
                    "description": exp.description,
                }
            )

        # Projects'i ekle
        for proj in projects:
            context["projects"].append(
                {
                    "id": proj.id,
                    "title": proj.title,
                    "description": proj.description,
                    "tech_stack": _parse_json(proj.tech_stack, []),
                    "url": proj.url,
                }
            )

        # Eğitim kayıtlarını ekle
        for edu in education_records:
            context["education"].append(
                {
                    "id": edu.id,
                    "school": edu.school,
                    "degree": edu.degree,
                    "field_of_study": edu.field_of_study,
                    "start_date": edu.start_date.isoformat() if edu.start_date else None,
                    "end_date": edu.end_date.isoformat() if edu.end_date else None,
                    "description": edu.description,
                }
            )

        logger.info(
            "context_loaded",
            user_id=user_id,
            listing_id=listing_id,
            has_match=match is not None,
            experiences_count=len(experiences),
            projects_count=len(projects),
            education_count=len(education_records),
        )

        return context


def get_context_manager(db: AsyncSession) -> ContextManager:
    """ContextManager singleton factory"""
    return ContextManager(db)
