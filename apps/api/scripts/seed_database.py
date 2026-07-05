"""Gerçekçi demo verisiyle veritabanını seed eder.

Çalıştır: python scripts/seed_database.py (apps/api içinden, PYTHONPATH=. ile)
veya: docker compose exec -e PYTHONPATH=/app api python scripts/seed_database.py
"""
import asyncio
import json

from app.database import AsyncSessionLocal
from app.models import Document, JobListing, Match, User
from app.services.auth import get_password_hash
from sqlalchemy import delete

USERS = [
    dict(
        email="junior.dev@example.com",
        full_name="Ayşe Yılmaz",
        target_position="Backend Developer Intern",
        seniority="junior",
        experience_years=0.5,
        skills=["Python", "SQL", "Git", "REST API"],
        experience_summary="Üniversite projelerinde Flask ile 2 küçük API geliştirdi.",
        tone_preference="professional",
    ),
    dict(
        email="mid.dev@example.com",
        full_name="Mehmet Kaya",
        target_position="Full Stack Developer",
        seniority="mid",
        experience_years=2.5,
        skills=["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
        experience_summary="2 yıl bir fintech startup'ında full stack geliştirici olarak çalıştı.",
        tone_preference="confident",
    ),
    dict(
        email="senior.dev@example.com",
        full_name="Zeynep Demir",
        target_position="Senior Backend Engineer",
        seniority="senior",
        experience_years=5.0,
        skills=["Python", "FastAPI", "Kubernetes", "AWS", "System Design", "PostgreSQL"],
        experience_summary="5 yıl kıdemli backend mühendisi, mikroservis mimarileri kurdu.",
        tone_preference="professional",
    ),
]

LISTINGS = [
    dict(
        title="Backend Developer Intern",
        company="TechNova",
        raw_text=(
            "TechNova olarak yaz stajyeri arıyoruz. Gereken: Python, temel SQL bilgisi, "
            "Git kullanımı. Tercih sebebi: REST API deneyimi, FastAPI bilgisi."
        ),
    ),
    dict(
        title="Full Stack Developer",
        company="Kodçu Yazılım",
        raw_text=(
            "Full stack geliştirici arıyoruz. Zorunlu: Python, React, PostgreSQL. "
            "Tercih sebebi: Docker, CI/CD deneyimi. 1-3 yıl deneyim bekleniyor."
        ),
    ),
    dict(
        title="Senior Backend Engineer",
        company="ScaleUp Tech",
        raw_text=(
            "Kıdemli backend mühendisi arıyoruz. Zorunlu: Python, Kubernetes, sistem "
            "tasarımı deneyimi, AWS. Tercih sebebi: mikroservis mimarisi tecrübesi. 5+ yıl deneyim."
        ),
    ),
    dict(
        title="Data Engineer Intern",
        company="DataFlow",
        raw_text=(
            "Veri mühendisliği stajyeri arıyoruz. Zorunlu: Python, SQL. "
            "Tercih sebebi: Airflow, Spark bilgisi."
        ),
    ),
    dict(
        title="AI/ML Engineer",
        company="NeuralWorks",
        raw_text=(
            "Yapay zeka mühendisi arıyoruz. Zorunlu: Python, LLM API deneyimi (Gemini/OpenAI), "
            "FastAPI. Tercih sebebi: agent orkestrasyonu, prompt engineering. 2+ yıl deneyim."
        ),
    ),
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        # Eski veriyi temizle (bağımlılık sırasına göre: documents/matches -> listings/users)
        await session.execute(delete(Document))
        await session.execute(delete(Match))
        await session.execute(delete(JobListing))
        await session.execute(delete(User))
        await session.commit()

        users = []
        for u in USERS:
            user = User(
                email=u["email"],
                full_name=u["full_name"],
                hashed_password=get_password_hash("seedpass123"),
                target_position=u["target_position"],
                seniority=u["seniority"],
                experience_years=u["experience_years"],
                skills=json.dumps(u["skills"]),
                experience_summary=u["experience_summary"],
                tone_preference=u["tone_preference"],
            )
            session.add(user)
            users.append(user)

        listings = []
        for listing_data in LISTINGS:
            listing = JobListing(
                title=listing_data["title"],
                company=listing_data["company"],
                raw_text=listing_data["raw_text"],
                analysis_status="pending",
            )
            session.add(listing)
            listings.append(listing)

        await session.commit()

        print(f"Seeded {len(users)} users, {len(listings)} listings")
        for u in users:
            print(f"  - {u.email} ({u.seniority})")


if __name__ == "__main__":
    asyncio.run(seed())
