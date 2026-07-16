"""Gerçekçi demo verisiyle veritabanını seed eder.

Çalıştır: python scripts/seed_database.py (apps/api içinden, PYTHONPATH=. ile)
veya: docker compose exec -e PYTHONPATH=/app api python scripts/seed_database.py

Kullanıcılar bilinçli olarak farklı ünvan/tech-stack kombinasyonlarıyla seçildi
(Python Backend, Java Backend, AI Engineer, çoklu-stack Full Stack) ki CV/önyazı
ajanları ve eşleştirme skoru gerçekçi çeşitlilikte test edilebilsin. "Can Öztürk"
özellikle üç farklı dilde (C#, Java, Python) proje sahibi - CV ajanının ilana en
alakalı projeyi seçtiğini doğrulamak için (bkz. app/agents/cv_generation.py
_rank_projects).
"""
import asyncio
import json
from datetime import date

from sqlalchemy import delete

from app.database import AsyncSessionLocal
from app.models import (
    Document,
    EducationRecord,
    JobListing,
    Match,
    Project,
    User,
    WorkExperience,
)
from app.services.auth import get_password_hash

USERS = [
    dict(
        email="junior.dev@example.com",
        full_name="Ayşe Yılmaz",
        target_position="Python Backend Developer Intern",
        seniority="junior",
        experience_years=0.5,
        skills=["Python", "SQL", "Git", "REST API"],
        experience_summary="Üniversite projelerinde Flask ile 2 küçük API geliştirdi.",
        tone_preference="professional",
        gender="Kadın",
        nationality="TC",
        driver_license="B",
        military_status=None,
        birth_year=2003,
        education=[
            dict(
                school="Erzincan Binali Yıldırım Üniversitesi",
                degree="Lisans",
                field_of_study="Bilgisayar Mühendisliği",
                start_date=date(2021, 9, 1),
                end_date=None,
                description="4. sınıf, mezuniyet 2026 Haziran.",
            ),
        ],
        experiences=[
            dict(
                company="Üniversite Bitirme Projesi",
                title="Stajyer Geliştirici",
                start_date=date(2025, 6, 1),
                end_date=date(2025, 9, 1),
                description=(
                    "Flask ile küçük ölçekli bir REST API "
                    "ve SQLite entegrasyonu geliştirdi."
                ),
            )
        ],
        projects=[
            dict(
                title="Kütüphane Ödünç Takip API'si",
                description=(
                    "Flask + SQLite ile kitap ödünç/iade süreçlerini "
                    "yöneten basit bir REST API."
                ),
                tech_stack=["Python", "Flask", "SQLite"],
                url="https://github.com/example/library-api",
            ),
        ],
    ),
    dict(
        email="java.dev@example.com",
        full_name="Mehmet Kaya",
        target_position="Java Backend Developer",
        seniority="mid",
        experience_years=2.5,
        skills=["Java", "Spring Boot", "PostgreSQL", "Docker", "Kafka"],
        experience_summary=(
            "2 yıl bir fintech şirketinde Java/Spring "
            "Boot ile mikroservis geliştirdi."
        ),
        tone_preference="confident",
        gender="Erkek",
        nationality="TC",
        driver_license="B",
        military_status="Yapıldı",
        birth_year=1997,
        education=[
            dict(
                school="Orta Doğu Teknik Üniversitesi",
                degree="Lisans",
                field_of_study="Bilgisayar Mühendisliği",
                start_date=date(2015, 9, 1),
                end_date=date(2019, 6, 1),
                description=None,
            ),
        ],
        experiences=[
            dict(
                company="FinTechCo",
                title="Java Backend Developer",
                start_date=date(2023, 3, 1),
                end_date=None,
                description=(
                    "Spring Boot mikroservisleri geliştirdi, Kafka "
                    "ile event-driven mimariye geçişte çalıştı."
                ),
            )
        ],
        projects=[
            dict(
                title="Ödeme Mikroservisi",
                description="Spring Boot + Kafka ile asenkron ödeme işleme servisi.",
                tech_stack=["Java", "Spring Boot", "Kafka", "PostgreSQL"],
                url="https://github.com/example/payment-service",
            ),
            dict(
                title="Bildirim Servisi",
                description="Kullanıcı bildirimlerini yöneten, Redis kuyruklu Spring Boot servisi.",
                tech_stack=["Java", "Spring Boot", "Redis"],
                url="https://github.com/example/notification-service",
            ),
        ],
    ),
    dict(
        email="ai.engineer@example.com",
        full_name="Zeynep Demir",
        target_position="AI Engineer",
        seniority="senior",
        experience_years=4.0,
        skills=[
            "Python",
            "LLM",
            "Gemini API",
            "FastAPI",
            "Prompt Engineering",
            "LangChain",
        ],
        experience_summary=(
            "4 yıl backend deneyiminin son 1.5 yılında LLM tabanlı agent sistemleri "
            "geliştirmeye odaklandı."
        ),
        tone_preference="professional",
        gender="Kadın",
        nationality="TC",
        driver_license="B",
        military_status=None,
        birth_year=1996,
        education=[
            dict(
                school="Boğaziçi Üniversitesi",
                degree="Yüksek Lisans",
                field_of_study="Yapay Zeka",
                start_date=date(2019, 9, 1),
                end_date=date(2021, 6, 1),
                description=None,
            ),
            dict(
                school="Boğaziçi Üniversitesi",
                degree="Lisans",
                field_of_study="Bilgisayar Mühendisliği",
                start_date=date(2015, 9, 1),
                end_date=date(2019, 6, 1),
                description=None,
            ),
        ],
        experiences=[
            dict(
                company="NeuralWorks",
                title="AI Engineer",
                start_date=date(2024, 6, 1),
                end_date=None,
                description=(
                    "Gemini function calling ile multi-agent "
                    "bir başvuru platformu geliştirdi."
                ),
            ),
            dict(
                company="ScaleUp Tech",
                title="Backend Developer",
                start_date=date(2021, 9, 1),
                end_date=date(2024, 5, 1),
                description=(
                    "FastAPI tabanlı servislerde çalıştı, sonrasında "
                    "AI ürünlerine geçiş yaptı."
                ),
            ),
        ],
        projects=[
            dict(
                title="Çok Ajanlı Başvuru Asistanı",
                description=(
                    "Gemini function calling ile ilan analizi, eşleştirme, "
                    "CV ve önyazı üreten agent sistemi."
                ),
                tech_stack=["Python", "Gemini API", "FastAPI", "LangChain"],
                url="https://github.com/example/multi-agent-assistant",
            ),
            dict(
                title="Prompt Değerlendirme Aracı",
                description=(
                    "Farklı prompt varyantlarının çıktı kalitesini "
                    "otomatik skorlayan araç."
                ),
                tech_stack=["Python", "LLM", "Prompt Engineering"],
                url="https://github.com/example/prompt-eval",
            ),
        ],
    ),
    dict(
        email="fullstack.multi@example.com",
        full_name="Can Öztürk",
        target_position="Full Stack Developer",
        seniority="mid",
        experience_years=3.0,
        skills=["C#", "Java", "Python", "React", "SQL Server"],
        experience_summary=(
            "3 yıl boyunca farklı şirketlerde farklı teknoloji yığınlarıyla (C#, Java, Python) "
            "full stack projeler geliştirdi."
        ),
        tone_preference="confident",
        gender="Erkek",
        nationality="TC",
        driver_license="B",
        military_status="Muaf",
        birth_year=1998,
        education=[
            dict(
                school="Yıldız Teknik Üniversitesi",
                degree="Lisans",
                field_of_study="Yazılım Mühendisliği",
                start_date=date(2016, 9, 1),
                end_date=date(2021, 6, 1),
                description=None,
            ),
        ],
        experiences=[
            dict(
                company="Kodçu Yazılım",
                title="Full Stack Developer",
                start_date=date(2022, 1, 1),
                end_date=None,
                description=(
                    "React frontend + çoklu backend teknolojisiyle "
                    "(C#, Java, Python) projeler geliştirdi."
                ),
            )
        ],
        # Kasıtlı: 3 ayrı proje, 3 ayrı dil - CV ajanının ilana göre doğru
        # projeyi seçip seçmediğini test etmek için (US: "biri C# biri Java
        # biri Python kullanılan 3 ayrı projesi olduğunda").
        projects=[
            dict(
                title="Stok Yönetim Sistemi",
                description="ASP.NET Core + SQL Server ile kurumsal stok yönetim uygulaması.",
                tech_stack=["C#", "ASP.NET Core", "SQL Server"],
                url="https://github.com/example/inventory-dotnet",
            ),
            dict(
                title="Sipariş Takip Servisi",
                description="Spring Boot ile mikroservis mimarili sipariş takip API'si.",
                tech_stack=["Java", "Spring Boot", "PostgreSQL"],
                url="https://github.com/example/order-tracking-java",
            ),
            dict(
                title="Veri Analiz Panosu",
                description="FastAPI + React ile satış verilerini görselleştiren dashboard.",
                tech_stack=["Python", "FastAPI", "React"],
                url="https://github.com/example/sales-dashboard-python",
            ),
        ],
    ),
    dict(
        email="senior.dev@example.com",
        full_name="Elif Aydın",
        target_position="Senior Backend Engineer",
        seniority="senior",
        experience_years=5.0,
        skills=[
            "Python",
            "FastAPI",
            "Kubernetes",
            "AWS",
            "System Design",
            "PostgreSQL",
        ],
        experience_summary="5 yıl kıdemli backend mühendisi, mikroservis mimarileri kurdu.",
        tone_preference="professional",
        gender="Kadın",
        nationality="TC",
        driver_license=None,
        military_status=None,
        birth_year=1994,
        education=[
            dict(
                school="İstanbul Teknik Üniversitesi",
                degree="Lisans",
                field_of_study="Bilgisayar Mühendisliği",
                start_date=date(2012, 9, 1),
                end_date=date(2016, 6, 1),
                description=None,
            ),
        ],
        experiences=[
            dict(
                company="ScaleUp Tech",
                title="Senior Backend Engineer",
                start_date=date(2020, 4, 1),
                end_date=None,
                description=(
                    "AWS üzerinde Kubernetes ile ölçeklenen "
                    "mikroservis mimarisi tasarladı."
                ),
            )
        ],
        projects=[
            dict(
                title="Mikroservis Altyapı Geçişi",
                description="Monolitik sistemi Kubernetes tabanlı mikroservislere taşıyan proje.",
                tech_stack=["Python", "Kubernetes", "AWS", "FastAPI"],
                url="https://github.com/example/microservices-migration",
            ),
        ],
    ),
]

LISTINGS = [
    dict(
        title="Backend Developer Intern",
        company="TechNova",
        owner_email="junior.dev@example.com",
        raw_text=(
            "TechNova olarak yaz stajyeri arıyoruz. Gereken: Python, temel SQL bilgisi, "
            "Git kullanımı. Tercih sebebi: REST API deneyimi, FastAPI bilgisi."
        ),
        required_skills=["Python", "SQL", "Git"],
        nice_to_have_skills=["REST API", "FastAPI"],
        seniority="junior",
    ),
    dict(
        title="Java Backend Developer",
        company="FinTechCo",
        owner_email="java.dev@example.com",
        raw_text=(
            "Java Backend Developer arıyoruz. Zorunlu: Java, Spring Boot, PostgreSQL. "
            "Tercih sebebi: Kafka, Docker deneyimi. 2-4 yıl deneyim bekleniyor."
        ),
        required_skills=["Java", "Spring Boot", "PostgreSQL"],
        nice_to_have_skills=["Kafka", "Docker"],
        seniority="mid",
    ),
    dict(
        title="Full Stack Developer",
        company="Kodçu Yazılım",
        owner_email="fullstack.multi@example.com",
        raw_text=(
            "Full stack geliştirici arıyoruz. Zorunlu: Python, React, PostgreSQL. "
            "Tercih sebebi: Docker, CI/CD deneyimi. 1-3 yıl deneyim bekleniyor."
        ),
        required_skills=["Python", "React", "PostgreSQL"],
        nice_to_have_skills=["Docker", "CI/CD"],
        seniority="mid",
    ),
    dict(
        title="Senior Backend Engineer",
        company="ScaleUp Tech",
        owner_email="senior.dev@example.com",
        raw_text=(
            "Kıdemli backend mühendisi arıyoruz. Zorunlu: Python, Kubernetes, sistem "
            "tasarımı deneyimi, AWS. Tercih sebebi: mikroservis mimarisi tecrübesi. 5+ yıl deneyim."
        ),
        required_skills=["Python", "Kubernetes", "sistem tasarımı", "AWS"],
        nice_to_have_skills=["mikroservis mimarisi"],
        seniority="senior",
    ),
    dict(
        title="Data Engineer Intern",
        company="DataFlow",
        owner_email="junior.dev@example.com",
        raw_text=(
            "Veri mühendisliği stajyeri arıyoruz. Zorunlu: Python, SQL. "
            "Tercih sebebi: Airflow, Spark bilgisi."
        ),
        required_skills=["Python", "SQL"],
        nice_to_have_skills=["Airflow", "Spark"],
        seniority="junior",
    ),
    dict(
        title="AI/ML Engineer",
        company="NeuralWorks",
        owner_email="ai.engineer@example.com",
        raw_text=(
            "Yapay zeka mühendisi arıyoruz. Zorunlu: Python, LLM API deneyimi (Gemini/OpenAI), "
            "FastAPI. Tercih sebebi: agent orkestrasyonu, prompt engineering. 2+ yıl deneyim."
        ),
        required_skills=["Python", "LLM API", "FastAPI"],
        nice_to_have_skills=["agent orkestrasyonu", "prompt engineering"],
        seniority="mid",
    ),
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        # Eski veriyi temizle (bağımlılık sırasına göre)
        await session.execute(delete(Document))
        await session.execute(delete(Match))
        await session.execute(delete(Project))
        await session.execute(delete(WorkExperience))
        await session.execute(delete(EducationRecord))
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
                skills=json.dumps(u["skills"], ensure_ascii=False),
                experience_summary=u["experience_summary"],
                tone_preference=u["tone_preference"],
                gender=u.get("gender"),
                nationality=u.get("nationality"),
                driver_license=u.get("driver_license"),
                military_status=u.get("military_status"),
                birth_year=u.get("birth_year"),
            )
            session.add(user)
            users.append(user)
        await session.commit()

        for u, user in zip(USERS, users):
            for edu in u.get("education") or []:
                session.add(
                    EducationRecord(
                        user_id=user.id,
                        school=edu["school"],
                        degree=edu.get("degree"),
                        field_of_study=edu.get("field_of_study"),
                        start_date=edu.get("start_date"),
                        end_date=edu.get("end_date"),
                        description=edu.get("description"),
                    )
                )
            for exp in u.get("experiences") or []:
                session.add(
                    WorkExperience(
                        user_id=user.id,
                        company=exp["company"],
                        title=exp["title"],
                        start_date=exp.get("start_date"),
                        end_date=exp.get("end_date"),
                        description=exp.get("description"),
                    )
                )
            for proj in u.get("projects") or []:
                session.add(
                    Project(
                        user_id=user.id,
                        title=proj["title"],
                        description=proj.get("description"),
                        tech_stack=json.dumps(
                            proj.get("tech_stack") or [], ensure_ascii=False
                        ),
                        url=proj.get("url"),
                    )
                )
        await session.commit()

        # US-040 sonrası sahipsiz ilan hiçbir akışta kullanılamıyor - her seed
        # ilanı, profili o ilana en uygun seed kullanıcısına atanır ki demo
        # kullanıcıları giriş yapınca "İlanlarım"da hazır ilan bulup match/CV/
        # önyazı akışını deneyebilsin. required_skills/nice_to_have_skills önceden
        # dolduruluyor ve analysis_status="completed" veriliyor - "pending" bir
        # ilanda calculate_exact_score boş required_skills'i "kriter yok, tam
        # puan" sayıp yanıltıcı yüksek skor üretiyordu (ör. eşleşen/eksik beceri
        # listeleri boşken %90 uygunluk); /api/match artık analiz tamamlanmamış
        # ilanlarda 422 döndürüyor, bu yüzden seed ilanları gerçekten analiz
        # edilmiş gibi gelmeli.
        users_by_email = {u.email: u for u in users}
        listings = []
        for listing_data in LISTINGS:
            owner = users_by_email[listing_data["owner_email"]]
            listing = JobListing(
                created_by=owner.id,
                title=listing_data["title"],
                company=listing_data["company"],
                raw_text=listing_data["raw_text"],
                required_skills=json.dumps(
                    listing_data["required_skills"], ensure_ascii=False
                ),
                nice_to_have_skills=json.dumps(
                    listing_data["nice_to_have_skills"], ensure_ascii=False
                ),
                seniority=listing_data["seniority"],
                analysis_status="completed",
            )
            session.add(listing)
            listings.append(listing)

        await session.commit()

        # Demo eşleştirme + doküman kayıtları (US-010 borcu: matches/documents seed)
        demo_match = Match(
            user_id=users[0].id,
            listing_id=listings[0].id,
            score=72.5,
            matched_skills=json.dumps(["python", "sql", "git"], ensure_ascii=False),
            missing_skills=json.dumps(["docker"], ensure_ascii=False),
        )
        demo_doc = Document(
            user_id=users[0].id,
            listing_id=listings[0].id,
            doc_type="cover_letter",
            cover_letter_text=(
                "Sayın Yetkili, ilanınızda aradığınız Python ve SQL becerilerine "
                "üniversite projelerimde edindiğim deneyimle sahibim... (demo verisi)"
            ),
        )
        session.add_all([demo_match, demo_doc])
        await session.commit()

        total_experiences = sum(len(u.get("experiences") or []) for u in USERS)
        total_projects = sum(len(u.get("projects") or []) for u in USERS)
        total_education = sum(len(u.get("education") or []) for u in USERS)
        print(
            f"Seeded {len(users)} users, {len(listings)} listings, "
            f"{total_experiences} work experiences, {total_projects} projects, "
            f"{total_education} education records, 1 match, 1 document"
        )
        for u in users:
            print(f"  - {u.email} ({u.seniority}, {u.target_position})")


if __name__ == "__main__":
    asyncio.run(seed())
