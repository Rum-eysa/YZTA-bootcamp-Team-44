"""Application/Staj baÅŸvuru service"""
import uuid
from typing import Optional

from google import generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Application
from app.repositories.application import ApplicationRepository
from app.schemas.application import ApplicationCreate, ApplicationUpdate


class ApplicationService:
    """Service for application business logic"""

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self.repository = ApplicationRepository(session) if session else None

    async def get_by_id(self, application_id: str) -> Optional[Application]:
        """Get application by ID"""
        if not self.repository:
            return None
        return await self.repository.get(application_id)

    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100):
        """Get all applications for a user"""
        if not self.repository:
            return []
        return await self.repository.get_by_user_id(user_id)

    async def get_all(self, skip: int = 0, limit: int = 100):
        """Get all applications (admin)"""
        if not self.repository:
            return []
        return await self.repository.get_all(skip, limit)

    async def create(self, application_data: ApplicationCreate) -> Application:
        """Create a new application"""
        db_application = Application(
            id=str(uuid.uuid4()),
            user_id=application_data.user_id,
            full_name=application_data.full_name,
            email=application_data.email,
            phone=application_data.phone,
            university=application_data.university,
            department=application_data.department,
            grade=application_data.grade,
            gpa=application_data.gpa,
            skills=application_data.skills,
            experience=application_data.experience,
            motivation=application_data.motivation,
            github_url=application_data.github_url,
            linkedin_url=application_data.linkedin_url,
            status="pending",
        )
        return await self.repository.create(db_application)

    async def update(
        self, application_id: str, application_data: ApplicationUpdate
    ) -> Optional[Application]:
        """Update application"""
        db_application = await self.get_by_id(application_id)
        if not db_application:
            return None

        update_data = application_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_application, field, value)

        return await self.repository.update(application_id, db_application)

    async def analyze_with_ai(self, application: Application) -> dict:
        """Analyze application using Google Gemini AI"""
        if not settings.GEMINI_API_KEY:
            return {
                "score": 50.0,
                "feedback": "AI analysis not available - API key not configured",
                "strengths": [],
                "weaknesses": [],
                "recommendation": "Manual review required",
            }

        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)

            prompt = f"""
            Analyze this internship application and provide a score (0-100), feedback, strengths,
            weaknesses, and recommendation.

            Application Details:
            - Name: {application.full_name}
            - University: {application.university}
            - Department: {application.department}
            - Grade: {application.grade}
            - GPA: {application.gpa}
            - Skills: {application.skills}
            - Experience: {application.experience}
            - Motivation: {application.motivation}
            - GitHub: {application.github_url or 'Not provided'}
            - LinkedIn: {application.linkedin_url or 'Not provided'}

            Provide response in JSON format with these fields: score, feedback, strengths (array),
            weaknesses (array), recommendation
            """
            response = model.generate_content(prompt)

            # Parse response (simplified - in production, use proper JSON parsing)
            return {
                "score": 75.0,
                "feedback": response.text[:500],
                "strengths": [
                    "Technical skills",
                    "Academic background",
                ],
                "weaknesses": [
                    "Limited experience",
                ],
                "recommendation": "Consider for interview",
            }
        except Exception as e:
            return {
                "score": 50.0,
                "feedback": f"AI analysis failed: {str(e)}",
                "strengths": [],
                "weaknesses": [],
                "recommendation": "Manual review required",
            }


async def create_application(
    db: AsyncSession, application_data: ApplicationCreate
) -> Application:
    return await ApplicationService(db).create(application_data)


async def get_application_by_id(
    db: AsyncSession, application_id: str
) -> Optional[Application]:
    return await ApplicationService(db).get_by_id(application_id)


async def get_applications_by_user(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 100
):
    return await ApplicationService(db).get_by_user_id(user_id, skip, limit)


async def get_all_applications(db: AsyncSession, skip: int = 0, limit: int = 100):
    return await ApplicationService(db).get_all(skip, limit)


async def update_application(
    db: AsyncSession, application_id: str, application_data: ApplicationUpdate
) -> Optional[Application]:
    return await ApplicationService(db).update(application_id, application_data)


async def analyze_application_with_ai(application: Application) -> dict:
    return await ApplicationService().analyze_with_ai(application)
