"""CV Ajanı testleri: LaTeX escape güvenliği + retry mantığı (mock subprocess/Tectonic yok)"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.agents.cv_generation import (
    CVGenerationAgent,
    CVGenerationException,
    _rank_projects,
    _sorted_education,
    _sorted_experiences,
    get_cv_generation_agent,
    latex_escape,
)
from app.exceptions import ValidationException


def test_latex_escape_handles_special_characters():
    """LaTeX'i kırabilecek karakterler (# _ % & { } gibi) kaçışlanmalı"""
    dangerous = "50% skor & #1 adayım {vurgu} deneyim_yılı"
    escaped = latex_escape(dangerous)

    assert r"\%" in escaped
    assert r"\&" in escaped
    assert r"\#" in escaped
    assert r"\_" in escaped
    assert r"\{" in escaped
    assert r"\}" in escaped
    # ham özel karakterler tek başına kalmamalı (backslash'siz)
    assert "50\\% skor \\& \\#1" in escaped


def test_latex_escape_handles_none_and_empty():
    assert latex_escape(None) == ""
    assert latex_escape("") == ""


@pytest.mark.asyncio
async def test_generate_missing_profile_raises_validation_error():
    agent = CVGenerationAgent(storage=MagicMock())

    with pytest.raises(ValidationException):
        await agent.generate({}, {"position_title": "Dev"})


@pytest.mark.asyncio
async def test_compile_retries_once_then_succeeds():
    """İlk deneme başarısız (dönüş kodu != 0), ikinci deneme başarılı olmalı"""
    agent = CVGenerationAgent(storage=MagicMock())

    call_count = {"n": 0}

    async def fake_create_subprocess_exec(*args, **kwargs):
        call_count["n"] += 1
        proc = MagicMock()
        if call_count["n"] == 1:
            proc.communicate = AsyncMock(return_value=(b"", b"fake latex error"))
            proc.returncode = 1
        else:
            # ikinci denemede tectonic --outdir hedefine gerçek bir dosya yazmadığımız
            # için burada sadece returncode=0 dönüp pdf_path.exists() kontrolünü
            # geçmesi için gerçek bir dosya oluşturuyoruz
            from pathlib import Path

            outdir = Path(args[3])  # tectonic tex.tex --outdir <dir>
            (outdir / "cv.pdf").write_bytes(b"%PDF-fake")
            proc.communicate = AsyncMock(return_value=(b"", b""))
            proc.returncode = 0
        return proc

    with patch("asyncio.create_subprocess_exec", side_effect=fake_create_subprocess_exec):
        pdf_bytes = await agent._compile_with_tectonic(
            "\\documentclass{article}\\begin{document}x\\end{document}"
        )

    assert pdf_bytes == b"%PDF-fake"
    assert call_count["n"] == 2


@pytest.mark.asyncio
async def test_compile_raises_clean_exception_after_all_retries_fail():
    agent = CVGenerationAgent(storage=MagicMock())

    async def always_fail(*args, **kwargs):
        proc = MagicMock()
        proc.communicate = AsyncMock(return_value=(b"", b"persistent latex error"))
        proc.returncode = 1
        return proc

    with patch("asyncio.create_subprocess_exec", side_effect=always_fail):
        with pytest.raises(CVGenerationException):
            await agent._compile_with_tectonic("broken tex", max_retries=2)


@pytest.mark.asyncio
async def test_generate_and_save_uploads_and_persists_document():
    storage = MagicMock()
    storage.upload_cv.return_value = "http://localhost:9000/cv-documents/cv/fake.pdf"
    agent = CVGenerationAgent(storage=storage)
    agent.generate = AsyncMock(return_value=b"%PDF-fake")
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    document = await agent.generate_and_save(
        db=db,
        user_id="user-1",
        listing_id="listing-1",
        user_profile={"full_name": "Ayşe"},
        job_analysis={"position_title": "Backend Developer"},
    )

    storage.upload_cv.assert_called_once_with("user-1", b"%PDF-fake")
    assert document.doc_type == "cv"
    assert document.cv_url == "http://localhost:9000/cv-documents/cv/fake.pdf"
    db.add.assert_called_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()


def test_cv_generation_exception_returns_422():
    """US-015: LaTeX/Tectonic hatası kullanıcıya 422 + temiz mesaj olarak dönmeli"""
    exc = CVGenerationException()
    assert exc.status_code == 422
    assert exc.error_code == "CV_GENERATION_ERROR"


@pytest.mark.asyncio
async def test_generate_rejects_non_pdf_output():
    """Tectonic PDF olmayan bir çıktı üretirse temiz bir hata fırlatılmalı (stack trace sızmaz)"""
    agent = CVGenerationAgent(storage=MagicMock())
    agent._compile_with_tectonic = AsyncMock(return_value=b"not-a-pdf")

    with pytest.raises(CVGenerationException):
        await agent.generate({"full_name": "Ayşe"}, {"position_title": "Dev"})


def test_get_cv_generation_agent_returns_singleton():
    assert get_cv_generation_agent() is get_cv_generation_agent()


def test_rank_projects_prioritizes_matching_tech_stack():
    """US: aday C#, Java ve Python projeleri olduğunda, ilana en uygun proje öne çıkmalı"""
    projects = [
        {"title": "Envanter Sistemi", "tech_stack": ["C#", ".NET"], "description": ""},
        {"title": "Mikroservis API", "tech_stack": ["Java", "Spring Boot"], "description": ""},
        {"title": "Veri Pipeline", "tech_stack": ["Python", "FastAPI"], "description": ""},
    ]
    job_analysis = {"required_skills": ["Python", "FastAPI"], "nice_to_have_skills": ["Docker"]}

    ranked = _rank_projects(projects, job_analysis, limit=3)

    assert ranked[0]["title"] == "Veri Pipeline"


def test_rank_projects_respects_limit():
    projects = [
        {"title": f"Proje {i}", "tech_stack": ["Python"], "description": ""} for i in range(5)
    ]
    ranked = _rank_projects(projects, {"required_skills": ["Python"]}, limit=3)
    assert len(ranked) == 3


def test_rank_projects_empty_list_returns_empty():
    assert _rank_projects([], {"required_skills": ["Python"]}, limit=3) == []


def test_rank_projects_stable_order_on_tie():
    """Skor eşitse orijinal sıra korunmalı (rastgele karışmamalı)"""
    projects = [
        {"title": "A", "tech_stack": [], "description": ""},
        {"title": "B", "tech_stack": [], "description": ""},
        {"title": "C", "tech_stack": [], "description": ""},
    ]
    ranked = _rank_projects(projects, {"required_skills": ["Go"]}, limit=3)
    assert [p["title"] for p in ranked] == ["A", "B", "C"]


def test_sorted_experiences_puts_current_job_first():
    experiences = [
        {"title": "Junior Dev", "end_date": "2022-01-01"},
        {"title": "Mid Dev", "end_date": None},  # halen çalışıyor
        {"title": "Intern", "end_date": "2020-06-01"},
    ]
    sorted_exp = _sorted_experiences(experiences)
    assert sorted_exp[0]["title"] == "Mid Dev"
    assert sorted_exp[-1]["title"] == "Intern"


@pytest.mark.asyncio
async def test_render_latex_includes_experience_and_selected_projects():
    """CV'de en alakalı proje(ler) ve iş deneyimi bölümü gerçekten basılmalı"""
    agent = CVGenerationAgent(storage=MagicMock())
    profile = {
        "full_name": "Ayşe Yılmaz",
        "skills": ["Python", "FastAPI"],
        "work_experiences": [
            {
                "company": "Acme",
                "title": "Backend Developer",
                "start_date": "2022-01-01",
                "end_date": None,
                "description": "FastAPI ile REST API geliştirdi.",
            }
        ],
        "projects": [
            {"title": "C# Envanter", "tech_stack": ["C#"], "description": "..."},
            {"title": "Python API", "tech_stack": ["Python", "FastAPI"], "description": "..."},
        ],
    }
    job_analysis = {"position_title": "Backend Developer", "required_skills": ["Python", "FastAPI"]}

    tex = agent._render_latex(profile, job_analysis)

    assert "Backend Developer" in tex
    assert "Acme" in tex
    assert "Python API" in tex
    # C# projesi bu ilanla alakasız değil ama Python API daha üstte olmalı
    assert tex.index("Python API") < tex.index("C\\# Envanter")


def test_sorted_education_puts_ongoing_first():
    education = [
        {"school": "Lise", "end_date": "2018-06-01"},
        {"school": "Üniversite (devam ediyor)", "end_date": None},
        {"school": "İlkokul", "end_date": "2010-06-01"},
    ]
    sorted_edu = _sorted_education(education)
    assert sorted_edu[0]["school"] == "Üniversite (devam ediyor)"
    assert sorted_edu[-1]["school"] == "İlkokul"


@pytest.mark.asyncio
async def test_render_latex_includes_education_and_personal_info():
    """CV'de eğitim ve kişisel bilgiler (yalnızca doluysa) basılmalı"""
    agent = CVGenerationAgent(storage=MagicMock())
    profile = {
        "full_name": "Mehmet Kaya",
        "skills": ["Java"],
        "gender": "Erkek",
        "nationality": "TC",
        "birth_year": 1997,
        "military_status": "Yapıldı",
        "driver_license": "B",
        "education": [
            {
                "school": "ODTÜ",
                "degree": "Lisans",
                "field_of_study": "Bilgisayar Mühendisliği",
                "start_date": "2015-09-01",
                "end_date": "2019-06-01",
            }
        ],
    }
    job_analysis = {"position_title": "Java Backend Developer"}

    tex = agent._render_latex(profile, job_analysis)

    assert "Eğitim" in tex
    assert "ODTÜ" in tex
    assert "Kişisel Bilgiler" in tex
    assert "Erkek" in tex
    assert "Askerlik Durumu" in tex


@pytest.mark.asyncio
async def test_render_latex_omits_empty_personal_fields():
    """Doldurulmamış kişisel alanlar (ör. askerlik/ehliyet) CV'de hiç görünmemeli"""
    agent = CVGenerationAgent(storage=MagicMock())
    profile = {
        "full_name": "Elif Aydın",
        "skills": ["Python"],
        "gender": "Kadın",
        "military_status": None,
        "driver_license": None,
    }
    tex = agent._render_latex(profile, {"position_title": "Senior Backend Engineer"})

    assert "Askerlik Durumu" not in tex
    assert "Sürücü Belgesi" not in tex
    assert "Cinsiyet" in tex


@pytest.mark.asyncio
async def test_render_latex_omits_education_section_when_empty():
    agent = CVGenerationAgent(storage=MagicMock())
    tex = agent._render_latex(
        {"full_name": "Ayşe", "skills": ["Python"]}, {"position_title": "Dev"}
    )
    assert "Eğitim" not in tex
    assert "Kişisel Bilgiler" not in tex
