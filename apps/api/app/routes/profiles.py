"""User profile routes (US-008 alias + US-013 experiences/projects CRUD)"""

import json
from typing import List

from app.database import get_db
from app.dependencies import get_current_user_id
from app.models import (
    Certificate,
    EducationRecord,
    Exam,
    Language,
    Project,
    Reference,
    SocialLink,
    WorkExperience,
)
from app.repositories.certificate import CertificateRepository
from app.repositories.education import EducationRepository
from app.repositories.exam import ExamRepository
from app.repositories.experience import WorkExperienceRepository
from app.repositories.language import LanguageRepository
from app.repositories.project import ProjectRepository
from app.repositories.reference import ReferenceRepository
from app.repositories.social_link import SocialLinkRepository
from app.routes.users import update_current_user
from app.schemas.certificate import CertificateCreate, CertificateResponse, CertificateUpdate
from app.schemas.education import EducationCreate, EducationResponse, EducationUpdate
from app.schemas.exam import ExamCreate, ExamResponse, ExamUpdate
from app.schemas.experience import (
    WorkExperienceCreate,
    WorkExperienceResponse,
    WorkExperienceUpdate,
)
from app.schemas.language import LanguageCreate, LanguageResponse, LanguageUpdate
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.reference import ReferenceCreate, ReferenceResponse, ReferenceUpdate
from app.schemas.social_link import SocialLinkCreate, SocialLinkResponse, SocialLinkUpdate
from app.schemas.user import UserResponse, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Profiles"])


@router.patch("/me", response_model=UserResponse)
async def patch_profile(
    user_update: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile (US-008 alias for PATCH /api/profiles/me)."""
    return await update_current_user(user_update, user_id, db)


# --- US-013: Work Experiences CRUD (JWT korumalı) ---


@router.get("/me/experiences", response_model=List[WorkExperienceResponse])
async def list_experiences(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Mevcut kullanıcının tüm iş deneyimlerini listeler."""
    repo = WorkExperienceRepository(db)
    return await repo.list_by_user(user_id)


@router.post(
    "/me/experiences",
    response_model=WorkExperienceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_experience(
    payload: WorkExperienceCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Yeni iş deneyimi ekler."""
    repo = WorkExperienceRepository(db)
    experience = WorkExperience(user_id=user_id, **payload.model_dump())
    return await repo.create(experience)


@router.patch("/me/experiences/{experience_id}", response_model=WorkExperienceResponse)
async def update_experience(
    experience_id: str,
    payload: WorkExperienceUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Bir iş deneyimini günceller (yalnızca sahibi)."""
    repo = WorkExperienceRepository(db)
    experience = await repo.get(experience_id)
    if not experience or experience.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(experience, field, value)
    return await repo.update(experience_id, experience)


@router.delete("/me/experiences/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(
    experience_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Bir iş deneyimini siler (yalnızca sahibi)."""
    repo = WorkExperienceRepository(db)
    experience = await repo.get(experience_id)
    if not experience or experience.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
    await repo.delete(experience_id)


# --- US-013: Projects CRUD (JWT korumalı) ---


@router.get("/me/projects", response_model=List[ProjectResponse])
async def list_projects(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Mevcut kullanıcının tüm projelerini listeler."""
    repo = ProjectRepository(db)
    return await repo.list_by_user(user_id)


@router.post(
    "/me/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    payload: ProjectCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Yeni proje ekler."""
    repo = ProjectRepository(db)
    data = payload.model_dump()
    if data.get("tech_stack") is not None:
        data["tech_stack"] = json.dumps(data["tech_stack"], ensure_ascii=False)
    project = Project(user_id=user_id, **data)
    return await repo.create(project)


@router.patch("/me/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Bir projeyi günceller (yalnızca sahibi)."""
    repo = ProjectRepository(db)
    project = await repo.get(project_id)
    if not project or project.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "tech_stack" in update_data and update_data["tech_stack"] is not None:
        update_data["tech_stack"] = json.dumps(update_data["tech_stack"], ensure_ascii=False)
    for field, value in update_data.items():
        setattr(project, field, value)
    return await repo.update(project_id, project)


@router.delete("/me/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Bir projeyi siler (yalnızca sahibi)."""
    repo = ProjectRepository(db)
    project = await repo.get(project_id)
    if not project or project.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    await repo.delete(project_id)


# --- Eğitim CRUD (JWT korumalı) ---


@router.get("/me/education", response_model=List[EducationResponse])
async def list_education(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = EducationRepository(db)
    return await repo.list_by_user(user_id)


@router.post(
    "/me/education",
    response_model=EducationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_education(
    payload: EducationCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = EducationRepository(db)
    record = EducationRecord(user_id=user_id, **payload.model_dump())
    return await repo.create(record)


@router.patch("/me/education/{education_id}", response_model=EducationResponse)
async def update_education(
    education_id: str,
    payload: EducationUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = EducationRepository(db)
    record = await repo.get(education_id)
    if not record or record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    return await repo.update(education_id, record)


@router.delete("/me/education/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    education_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = EducationRepository(db)
    record = await repo.get(education_id)
    if not record or record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")
    await repo.delete(education_id)


# --- Sertifikalar ---


@router.get("/me/certificates", response_model=List[CertificateResponse])
async def list_certificates(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = CertificateRepository(db)
    return await repo.list_by_user(user_id)


@router.post(
    "/me/certificates",
    response_model=CertificateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_certificate(
    payload: CertificateCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = CertificateRepository(db)
    cert = Certificate(user_id=user_id, **payload.model_dump())
    return await repo.create(cert)


@router.patch("/me/certificates/{certificate_id}", response_model=CertificateResponse)
async def update_certificate(
    certificate_id: str,
    payload: CertificateUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = CertificateRepository(db)
    cert = await repo.get(certificate_id)
    if not cert or cert.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(cert, field, value)
    return await repo.update(certificate_id, cert)


@router.delete("/me/certificates/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certificate(
    certificate_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = CertificateRepository(db)
    cert = await repo.get(certificate_id)
    if not cert or cert.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    await repo.delete(certificate_id)


# --- Sınavlar ---


@router.get("/me/exams", response_model=List[ExamResponse])
async def list_exams(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ExamRepository(db)
    return await repo.list_by_user(user_id)


@router.post("/me/exams", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def create_exam(
    payload: ExamCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ExamRepository(db)
    exam = Exam(user_id=user_id, **payload.model_dump())
    return await repo.create(exam)


@router.patch("/me/exams/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: str,
    payload: ExamUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ExamRepository(db)
    exam = await repo.get(exam_id)
    if not exam or exam.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(exam, field, value)
    return await repo.update(exam_id, exam)


@router.delete("/me/exams/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ExamRepository(db)
    exam = await repo.get(exam_id)
    if not exam or exam.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    await repo.delete(exam_id)


# --- Yabancı Dil ---


@router.get("/me/languages", response_model=List[LanguageResponse])
async def list_languages(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = LanguageRepository(db)
    return await repo.list_by_user(user_id)


@router.post("/me/languages", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
async def create_language(
    payload: LanguageCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = LanguageRepository(db)
    lang = Language(user_id=user_id, **payload.model_dump())
    return await repo.create(lang)


@router.patch("/me/languages/{language_id}", response_model=LanguageResponse)
async def update_language(
    language_id: str,
    payload: LanguageUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = LanguageRepository(db)
    lang = await repo.get(language_id)
    if not lang or lang.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(lang, field, value)
    return await repo.update(language_id, lang)


@router.delete("/me/languages/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_language(
    language_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = LanguageRepository(db)
    lang = await repo.get(language_id)
    if not lang or lang.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
    await repo.delete(language_id)


# --- Sosyal Bağlantılar ---


@router.get("/me/social-links", response_model=List[SocialLinkResponse])
async def list_social_links(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = SocialLinkRepository(db)
    return await repo.list_by_user(user_id)


@router.post(
    "/me/social-links",
    response_model=SocialLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_social_link(
    payload: SocialLinkCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = SocialLinkRepository(db)
    link = SocialLink(user_id=user_id, **payload.model_dump())
    return await repo.create(link)


@router.patch("/me/social-links/{social_link_id}", response_model=SocialLinkResponse)
async def update_social_link(
    social_link_id: str,
    payload: SocialLinkUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = SocialLinkRepository(db)
    link = await repo.get(social_link_id)
    if not link or link.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social link not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(link, field, value)
    return await repo.update(social_link_id, link)


@router.delete("/me/social-links/{social_link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_link(
    social_link_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = SocialLinkRepository(db)
    link = await repo.get(social_link_id)
    if not link or link.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social link not found")
    await repo.delete(social_link_id)


# --- Referanslar ---


@router.get("/me/references", response_model=List[ReferenceResponse])
async def list_references(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ReferenceRepository(db)
    return await repo.list_by_user(user_id)


@router.post(
    "/me/references",
    response_model=ReferenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reference(
    payload: ReferenceCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ReferenceRepository(db)
    ref = Reference(user_id=user_id, **payload.model_dump())
    return await repo.create(ref)


@router.patch("/me/references/{reference_id}", response_model=ReferenceResponse)
async def update_reference(
    reference_id: str,
    payload: ReferenceUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ReferenceRepository(db)
    ref = await repo.get(reference_id)
    if not ref or ref.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reference not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ref, field, value)
    return await repo.update(reference_id, ref)


@router.delete("/me/references/{reference_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reference(
    reference_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ReferenceRepository(db)
    ref = await repo.get(reference_id)
    if not ref or ref.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reference not found")
    await repo.delete(reference_id)
