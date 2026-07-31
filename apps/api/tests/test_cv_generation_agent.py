"""CV Ajanı testleri: LaTeX escape güvenliği + retry mantığı (mock subprocess/Tectonic yok)"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.agents.cv_generation import (
    CV_TEMPLATE_IDS,
    CVGenerationAgent,
    CVGenerationException,
    DEFAULT_CV_TEMPLATE,
    _MAX_DESCRIPTION_CHARS,
    _clamp_description,
    _format_month_year,
    _format_period,
    _languages_line,
    _rank_projects,
    _rewrites_to_map,
    _select_and_rewrite,
    _select_indices,
    _sorted_education,
    _sorted_experiences,
    get_cv_generation_agent,
    latex_escape,
    normalize_cv_template_id,
)
from app.exceptions import GeminiAPIException, ValidationException


class FakeGeminiClient:
    """generate_text çağrısını simüle eder, gönderilen prompt'u yakalar"""

    def __init__(self, fake_text: str = "Yapay zeka ile yazılmış kısa bir özet metni."):
        self.fake_text = fake_text
        self.last_prompt: str | None = None
        self.call_count = 0
        self.generate_text = AsyncMock(side_effect=self._generate)
        self.generate_json = AsyncMock(
            return_value={
                "experience_indices": [],
                "project_indices": [],
                "certificate_indices": [],
            }
        )

    async def _generate(self, prompt: str, temperature: float = 0.7):
        self.call_count += 1
        self.last_prompt = prompt
        return self.fake_text


class FailingGeminiClient:
    def __init__(self):
        self.generate_text = AsyncMock(side_effect=GeminiAPIException("quota exceeded"))
        self.generate_json = AsyncMock(side_effect=GeminiAPIException("quota exceeded"))


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


def test_format_month_year_turkish_month_and_year_only():
    assert _format_month_year("2024-06-01") == "Haziran 2024"
    assert _format_month_year("2023-09") == "Eylül 2023"
    assert _format_month_year(None) == ""
    assert _format_month_year("") == ""


def test_format_period_uses_month_year_and_devam_ediyor():
    assert (
        _format_period({"start_date": "2024-06-01", "end_date": "2024-09-15"})
        == "Haziran 2024 - Eylül 2024"
    )
    assert (
        _format_period({"start_date": "2025-09-01", "end_date": None})
        == "Eylül 2025 - devam ediyor"
    )


@pytest.mark.asyncio
async def test_render_latex_includes_education_section():
    """Version şablonlarında eğitim doluysa basılmalı; kişisel bilgiler bölümü yok"""
    agent = CVGenerationAgent(storage=MagicMock())
    profile = {
        "full_name": "Mehmet Kaya",
        "skills": ["Java"],
        "gender": "Erkek",
        "military_status": "Yapıldı",
        "education": [
            {
                "school": "ODTÜ",
                "degree": "Lisans",
                "field_of_study": "Bilgisayar Mühendisliği",
                "start_date": "2015-09-01",
                "end_date": "2019-06-01",
                "description": "Tez: dağıtık sistemler.",
            },
            {
                "school": "ODTÜ",
                "degree": "Yüksek Lisans",
                "field_of_study": "Yazılım Mühendisliği",
                "start_date": "2019-09-01",
                "end_date": "2021-06-01",
            },
        ],
    }
    job_analysis = {"position_title": "Java Backend Developer"}

    tex = agent._render_latex(profile, job_analysis)

    assert "Eğitimler" in tex
    assert "ODTÜ" in tex
    assert "Eylül 2015 - Haziran 2019" in tex
    assert "2015-09-01" not in tex
    assert "Kişisel Bilgiler" not in tex
    assert "Askerlik Durumu" not in tex
    # Her eğitim kaydı \par ile ayrılsın (açıklama sonrası kaymayı önler)
    assert tex.count(r"\par\noindent") >= 2
    assert "Tez: da" in tex
    assert r"\par\vspace" in tex


@pytest.mark.asyncio
async def test_render_latex_omits_education_section_when_empty():
    agent = CVGenerationAgent(storage=MagicMock())
    tex = agent._render_latex(
        {"full_name": "Ayşe", "skills": ["Python"]}, {"position_title": "Dev"}
    )
    assert "Eğitimler" not in tex
    assert "Kişisel Bilgiler" not in tex


@pytest.mark.asyncio
async def test_render_latex_includes_location_certificates_languages_social_and_references():
    """US-044: ContextManager'dan gelen tüm ek profil alanları şablona basılmalı"""
    agent = CVGenerationAgent(storage=MagicMock())
    profile = {
        "full_name": "Ayşe Yılmaz",
        "skills": ["Python"],
        "location": "İstanbul, Türkiye",
        "certificates": [
            {"title": "AWS Certified Developer", "issuer": "Amazon", "issue_date": "2023-05-01"}
        ],
        "languages": [
            {"name": "İngilizce", "level": "İleri"},
            {"name": "Almanca", "level": "Orta"},
        ],
        "social_links": [{"platform": "GitHub", "url": "https://github.com/ayse"}],
        "references": [{"name": "Mehmet Öz", "title": "Tech Lead", "company": "Acme"}],
    }
    tex = agent._render_latex(profile, {"position_title": "Dev"})

    assert "İstanbul, Türkiye" in tex
    assert "AWS Certified Developer" in tex
    assert "İngilizce (İleri) | Almanca (Orta)" in tex
    assert "\\item \\textbf{İngilizce}" not in tex
    assert "github.com/ayse" in tex
    assert "Mehmet Öz" in tex


def test_languages_line_joins_with_pipe():
    assert (
        _languages_line(
            [{"name": "İngilizce", "level": "İleri"}, {"name": "Almanca", "level": "Orta"}]
        )
        == "İngilizce (İleri) | Almanca (Orta)"
    )


def test_clamp_description_shortens_long_text():
    long = ("Python ile API geliştirdim. " * 40).strip()
    clamped = _clamp_description(long)
    assert len(clamped) <= _MAX_DESCRIPTION_CHARS + 1  # olası … için
    assert clamped != long


def test_select_and_rewrite_clamps_long_description():
    long = "x" * 500
    result = _select_and_rewrite([{"title": "P", "description": long}], [0], {})
    assert len(result[0]["description"]) <= _MAX_DESCRIPTION_CHARS + 1


@pytest.mark.asyncio
async def test_render_latex_has_photo_includes_includegraphics_version1():
    agent = CVGenerationAgent(storage=MagicMock())
    tex = agent._render_latex(
        {"full_name": "Ayşe", "skills": ["Python"]},
        {"position_title": "Dev"},
        cv_template="Version1",
        has_photo=True,
        avatar_filename="avatar.jpg",
    )
    assert "includegraphics" in tex
    assert "avatar.jpg" in tex
    assert r"\textbf{Fotoğraf}" not in tex


@pytest.mark.asyncio
async def test_render_latex_no_photo_shows_placeholder_version1():
    agent = CVGenerationAgent(storage=MagicMock())
    tex = agent._render_latex(
        {"full_name": "Ayşe", "skills": ["Python"]},
        {"position_title": "Dev"},
        cv_template="Version1",
        has_photo=False,
    )
    assert "Fotoğraf" in tex
    assert "Alanı" in tex
    assert "includegraphics" not in tex


@pytest.mark.asyncio
async def test_render_latex_does_not_print_job_requirements_section():
    """İlan becerileri filtre/rewrite/ranking için kullanılır; CV gövdesine ayrı bölüm basılmaz
    (1 sayfa hedefi + ATS CV gerçekçiliği)."""
    agent = CVGenerationAgent(storage=MagicMock())
    tex = agent._render_latex(
        {"full_name": "Ayşe", "skills": ["Python"]},
        {
            "position_title": "Dev",
            "required_skills": ["Python", "FastAPI"],
            "nice_to_have_skills": ["Docker"],
        },
    )

    assert "Hedef Pozisyon Gereksinimleri" not in tex
    assert "Aranan Beceriler" not in tex


@pytest.mark.asyncio
async def test_render_latex_omits_optional_sections_when_empty():
    agent = CVGenerationAgent(storage=MagicMock())
    tex = agent._render_latex(
        {"full_name": "Ayşe", "skills": ["Python"]}, {"position_title": "Dev"}
    )

    assert "Sertifikalar" not in tex
    assert "Sınavlar" not in tex
    assert "Yabancı Dil" not in tex
    assert "Referanslar" not in tex
    assert "Özgeçmiş Özeti" not in tex
    assert "Hedef Pozisyon Gereksinimleri" not in tex


def test_normalize_cv_template_id_accepts_version_and_legacy():
    assert normalize_cv_template_id("Version3") == "Version3"
    assert normalize_cv_template_id("1") == "Version1"
    assert normalize_cv_template_id("Version6") == "Version5"
    assert normalize_cv_template_id("bogus") == DEFAULT_CV_TEMPLATE
    assert normalize_cv_template_id(None) == DEFAULT_CV_TEMPLATE


@pytest.mark.asyncio
async def test_render_latex_selects_requested_version_template():
    agent = CVGenerationAgent(storage=MagicMock())
    profile = {"full_name": "Ayşe Yılmaz", "experience_summary": "Kısa özet"}

    tex_v1 = agent._render_latex(profile, {"position_title": "Dev"}, cv_template="Version1")
    tex_v4 = agent._render_latex(profile, {"position_title": "Dev"}, cv_template="Version4")
    tex_v5 = agent._render_latex(profile, {"position_title": "Dev"}, cv_template="Version5")

    assert "tikz" in tex_v1  # fotoğraf alanı
    assert "flushleft" in tex_v4  # fotoğrafsız sola yaslı
    assert "begin{center}" in tex_v5  # ortalanmış header
    assert "Ayşe Yılmaz" in tex_v1
    assert "Kısa özet" in tex_v1


@pytest.mark.asyncio
async def test_render_latex_all_version_templates_load():
    agent = CVGenerationAgent(storage=MagicMock())
    for template_id in CV_TEMPLATE_IDS:
        tex = agent._render_latex(
            {"full_name": "Test"}, {"position_title": "Dev"}, cv_template=template_id
        )
        assert "Test" in tex
        assert r"\begin{document}" in tex


@pytest.mark.asyncio
async def test_generate_passes_cv_template_into_render():
    agent = CVGenerationAgent(storage=MagicMock())
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")
    agent._render_latex = MagicMock(return_value=r"\documentclass{article}\begin{document}x\end{document}")

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        await agent.generate(
            {"full_name": "Ayşe"},
            {"position_title": "Dev"},
            cv_template="Version3",
        )

    assert agent._render_latex.call_args.kwargs["cv_template"] == "Version3"


@pytest.mark.asyncio
async def test_generate_raises_when_pdf_has_zero_pages():
    """US-015: PDF derlenmiş olsa da sayfa okunamıyorsa/0 sayfaysa temiz hata dönmeli"""
    agent = CVGenerationAgent(storage=MagicMock())
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake-no-pages")

    with pytest.raises(CVGenerationException, match="en az 1 sayfa"):
        await agent.generate({"full_name": "Ayşe"}, {"position_title": "Dev"})


@pytest.mark.asyncio
async def test_summary_always_uses_gemini_even_without_extra_prompt():
    """Belge dilinde özet için Gemini her zaman çağrılır (profil özeti TR kalsa bile)."""
    fake_client = FakeGeminiClient(fake_text="Experienced software engineer focused on backend systems.")
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        await agent.generate(
            {"full_name": "Ayşe", "experience_summary": "Orijinal özet"},
            {"position_title": "Dev", "document_language": "en"},
        )

    assert fake_client.call_count == 1
    tex_source = agent._compile_with_tectonic.call_args[0][0]
    assert "Experienced software engineer" in tex_source
    assert "Orijinal özet" not in tex_source


@pytest.mark.asyncio
async def test_extra_prompt_triggers_ai_summary_and_overrides_experience_summary():
    """US-050: extra_prompt verilirse Özet bölümü Gemini çıktısıyla değişmeli"""
    fake_client = FakeGeminiClient(fake_text="Takım çalışmasına yatkın, hızlı öğrenen bir aday.")
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        await agent.generate(
            {"full_name": "Ayşe", "experience_summary": "Orijinal özet"},
            {"position_title": "Dev"},
            extra_prompt="Takım çalışmasını vurgula",
        )

    assert fake_client.call_count == 1
    tex_source = agent._compile_with_tectonic.call_args[0][0]
    assert "Takım çalışmasına yatkın" in tex_source
    assert "Orijinal özet" not in tex_source
    assert "Takım çalışmasını vurgula" in fake_client.last_prompt
    assert '"""' in fake_client.last_prompt


@pytest.mark.asyncio
async def test_ai_summary_low_score_uses_potential_strategy():
    """US-050: eşleşme skoru düşükse CV özeti de potansiyel vurgusu stratejisini kullanmalı"""
    fake_client = FakeGeminiClient()
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        await agent.generate(
            {"full_name": "Ayşe"},
            {"position_title": "Dev"},
            matching_gaps={"score": 25},
            extra_prompt="motivasyonumu öne çıkar",
        )

    assert "POTANSİYEL vurgusu" in fake_client.last_prompt


@pytest.mark.asyncio
async def test_gemini_failure_falls_back_to_original_summary_without_failing():
    """US-050: Gemini kota/hata verirse CV üretimi başarısız olmamalı, orijinal özete dönülmeli"""
    agent = CVGenerationAgent(storage=MagicMock(), client=FailingGeminiClient())
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        pdf_bytes = await agent.generate(
            {"full_name": "Ayşe", "experience_summary": "Orijinal özet"},
            {"position_title": "Dev"},
            extra_prompt="Takım çalışmasını vurgula",
        )

    assert pdf_bytes == b"%PDF-fake"
    tex_source = agent._compile_with_tectonic.call_args[0][0]
    assert "Orijinal özet" in tex_source


@pytest.mark.asyncio
async def test_extra_prompt_reaches_generate_and_save():
    fake_client = FakeGeminiClient(fake_text="AI özet.")
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        await agent.generate_and_save(
            db=db,
            user_id="user-1",
            listing_id="listing-1",
            user_profile={"full_name": "Ayşe"},
            job_analysis={"position_title": "Dev"},
            extra_prompt="Staj motivasyonumu öne çıkar",
        )

    assert fake_client.call_count == 1
    assert "Staj motivasyonumu öne çıkar" in fake_client.last_prompt


# --- İçerik filtreleme (otomatik, ekip kararı) ------------------------------


def test_select_indices_empty_selection_falls_back_to_all():
    """LLM boş/geçersiz seçim döndürürse hiçbir şey kaybetmemeli - hepsini göster"""
    items = [{"title": "A"}, {"title": "B"}]
    assert _select_indices(items, []) == items
    assert _select_indices(items, [5, -1]) == items


def test_select_indices_applies_valid_subset():
    items = [{"title": "A"}, {"title": "B"}, {"title": "C"}]
    assert [i["title"] for i in _select_indices(items, [0, 2])] == ["A", "C"]


def test_select_indices_empty_items_returns_empty():
    assert _select_indices([], [0, 1]) == []


@pytest.mark.asyncio
async def test_no_filterable_content_never_calls_content_filter():
    """Profilde deneyim/proje/sertifika yoksa filtreleme için Gemini'ye hiç gidilmemeli"""
    fake_client = FakeGeminiClient()
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        await agent.generate({"full_name": "Ayşe"}, {"position_title": "Dev"})

    fake_client.generate_json.assert_not_called()


@pytest.mark.asyncio
async def test_filterable_content_triggers_content_filter_and_applies_selection():
    """Profilde deneyim/proje varsa LLM'e sorulmalı ve seçilen index'ler dışındaki
    öğeler CV'den çıkarılmalı"""
    fake_client = FakeGeminiClient()
    fake_client.generate_json = AsyncMock(
        return_value={"experience_indices": [1], "project_indices": [], "certificate_indices": []}
    )
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")
    profile = {
        "full_name": "Ayşe",
        "work_experiences": [
            {"title": "Muhasebe Uzmanı", "company": "X", "description": "Alakasız iş"},
            {"title": "Backend Developer", "company": "Y", "description": "FastAPI ile geliştirdi"},
        ],
    }

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        await agent.generate(profile, {"position_title": "Backend Developer"})

    fake_client.generate_json.assert_awaited_once()
    tex_source = agent._compile_with_tectonic.call_args[0][0]
    assert "Backend Developer" in tex_source
    assert "Muhasebe Uzmanı" not in tex_source


@pytest.mark.asyncio
async def test_extra_prompt_reaches_content_filter_as_edit_instructions():
    """Düzenleme notu filtre prompt'una içerik ekle/çıkar/kısalt olarak girmeli"""
    captured: dict[str, str] = {}

    async def capture_json(prompt: str, response_schema=None):
        captured["prompt"] = prompt
        return {
            "experience_indices": [0, 1],
            "project_indices": [],
            "certificate_indices": [],
            "experience_rewrites": [
                {"index": 0, "description": "kısa muhasebe"},
                {"index": 1, "description": "kısa backend"},
            ],
            "project_rewrites": [],
        }

    fake_client = FakeGeminiClient()
    fake_client.generate_json = AsyncMock(side_effect=capture_json)
    fake_client.generate_text = AsyncMock(return_value="Kısa özet.")
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")
    profile = {
        "full_name": "Ayşe",
        "work_experiences": [
            {"title": "Muhasebe Uzmanı", "company": "X", "description": "Alakasız uzun metin"},
            {"title": "Backend Developer", "company": "Y", "description": "FastAPI"},
        ],
    }

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        await agent.generate(
            profile,
            {"position_title": "Backend Developer"},
            extra_prompt="Muhasebe deneyimini tut ama kısalt",
        )

    assert "Muhasebe deneyimini tut ama kısalt" in captured["prompt"]
    assert "CV düzenleme notu" in captured["prompt"]
    assert "dahil etme veya çıkarma" in captured["prompt"]
    tex_source = agent._compile_with_tectonic.call_args[0][0]
    assert "Muhasebe Uzmanı" in tex_source
    assert "kısa muhasebe" in tex_source


@pytest.mark.asyncio
async def test_content_filter_failure_falls_back_to_showing_everything():
    """Gemini hata verirse (kota vb.) CV üretimi kırılmamalı, tüm içerik gösterilmeli"""
    failing_client = FailingGeminiClient()
    agent = CVGenerationAgent(storage=MagicMock(), client=failing_client)
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")
    profile = {
        "full_name": "Ayşe",
        "work_experiences": [{"title": "Backend Developer", "company": "Y", "description": "..."}],
    }

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        pdf_bytes = await agent.generate(profile, {"position_title": "Backend Developer"})

    assert pdf_bytes == b"%PDF-fake"
    tex_source = agent._compile_with_tectonic.call_args[0][0]
    assert "Backend Developer" in tex_source


# --- İlana göre yeniden yazma (tailoring) -----------------------------------


def test_rewrites_to_map_converts_valid_entries():
    entries = [{"index": 0, "description": "Yeni metin"}, {"index": 2, "description": "Başka"}]
    assert _rewrites_to_map(entries) == {0: "Yeni metin", 2: "Başka"}


def test_rewrites_to_map_ignores_invalid_entries():
    entries = [{"index": "abc", "description": "x"}, {"index": 1, "description": ""}, {}]
    assert _rewrites_to_map(entries) == {}


def test_select_and_rewrite_applies_rewrite_to_selected_item():
    items = [{"title": "A", "description": "orijinal"}, {"title": "B", "description": "orijinal"}]
    result = _select_and_rewrite(items, [0], {0: "yeniden yazılmış"})
    assert result == [{"title": "A", "description": "yeniden yazılmış"}]


def test_select_and_rewrite_applies_title_rewrite():
    items = [{"title": "Yazılım Mühendisi", "description": "orijinal"}]
    result = _select_and_rewrite(items, [0], {0: "Built APIs"}, {0: "Software Engineer"})
    assert result == [{"title": "Software Engineer", "description": "Built APIs"}]


def test_select_and_rewrite_keeps_original_when_no_rewrite_given():
    items = [{"title": "A", "description": "orijinal"}]
    result = _select_and_rewrite(items, [0], {})
    assert result == [{"title": "A", "description": "orijinal"}]


@pytest.mark.asyncio
async def test_render_latex_uses_tailored_description_when_provided():
    """İlana göre yeniden yazılan açıklama, orijinalin yerine CV'de basılmalı"""
    agent = CVGenerationAgent(storage=MagicMock())
    profile = {
        "full_name": "Ayşe",
        "work_experiences": [
            {"title": "Backend Developer", "company": "Y", "description": "orijinal açıklama"}
        ],
    }
    content_selection = {
        "experience_indices": [0],
        "project_indices": [],
        "certificate_indices": [],
        "experience_rewrites": {0: "ilana göre yeniden yazılmış açıklama"},
        "project_rewrites": {},
    }

    tex = agent._render_latex(profile, {"position_title": "Dev"}, None, content_selection)

    assert "ilana göre yeniden yazılmış açıklama" in tex
    assert "orijinal açıklama" not in tex


@pytest.mark.asyncio
async def test_content_filter_applies_tailored_rewrites_end_to_end():
    """generate() içinde LLM'in döndürdüğü rewrite CV'ye yansımalı"""
    fake_client = FakeGeminiClient()
    fake_client.generate_json = AsyncMock(
        return_value={
            "experience_indices": [0],
            "project_indices": [],
            "certificate_indices": [],
            "experience_rewrites": [{"index": 0, "description": "FastAPI ile ilana özel metin"}],
            "project_rewrites": [],
        }
    )
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")
    profile = {
        "full_name": "Ayşe",
        "work_experiences": [
            {"title": "Backend Developer", "company": "Y", "description": "genel açıklama"}
        ],
    }

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        await agent.generate(profile, {"position_title": "Backend Developer"})

    tex_source = agent._compile_with_tectonic.call_args[0][0]
    assert "FastAPI ile ilana özel metin" in tex_source
    assert "genel açıklama" not in tex_source


# --- 1 sayfayı aşan CV'yi kısaltma -------------------------------------------


@pytest.mark.asyncio
async def test_no_overflow_never_calls_fit():
    """PDF zaten 1 sayfaysa kısaltma/prune için ekstra adım yapılmamalı"""
    agent = CVGenerationAgent(storage=MagicMock())
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")
    agent._try_fit_to_one_page = AsyncMock(side_effect=AssertionError("çağrılmamalıydı"))

    with patch("app.agents.cv_generation._pdf_page_count", return_value=1):
        pdf_bytes = await agent.generate({"full_name": "Ayşe"}, {"position_title": "Dev"})

    assert pdf_bytes == b"%PDF-fake"


@pytest.mark.asyncio
async def test_overflow_triggers_shorten_and_recompiles_once():
    """PDF 1 sayfayı aşarsa kısaltma denenip yeniden derlenmeli, sonuç kısaltılmış olmalı"""
    fake_client = FakeGeminiClient()
    fake_client.generate_json = AsyncMock(
        side_effect=[
            {
                "experience_indices": [0],
                "project_indices": [],
                "certificate_indices": [],
                "experience_rewrites": [],
                "project_rewrites": [],
            },
            {
                "experience_rewrites": [{"index": 0, "description": "kısaltılmış açıklama"}],
                "project_rewrites": [],
            },
        ]
    )
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    agent._compile_with_tectonic = AsyncMock(
        side_effect=[b"%PDF-long", b"%PDF-short"]
    )
    profile = {
        "full_name": "Ayşe",
        "work_experiences": [
            {"title": "Backend Developer", "company": "Y", "description": "çok uzun açıklama"}
        ],
    }

    def page_count(pdf: bytes) -> int:
        return 1 if pdf == b"%PDF-short" else 2

    with patch("app.agents.cv_generation._pdf_page_count", side_effect=page_count):
        pdf_bytes = await agent.generate(profile, {"position_title": "Backend Developer"})

    assert pdf_bytes == b"%PDF-short"
    assert agent._compile_with_tectonic.await_count == 2
    second_tex = agent._compile_with_tectonic.call_args_list[1][0][0]
    assert "kısaltılmış açıklama" in second_tex
    assert "çok uzun açıklama" not in second_tex


@pytest.mark.asyncio
async def test_overflow_shorten_failure_falls_back_to_original_pdf():
    """Kısaltma çağrısı hata verirse orijinal (uzun) PDF hiç kaybedilmeden dönmeli.
    Deneyim-only profilde prune edilecek proje yok; ekstra derleme de olmaz."""
    fake_client = FakeGeminiClient()
    fake_client.generate_json = AsyncMock(
        side_effect=[
            {
                "experience_indices": [0],
                "project_indices": [],
                "certificate_indices": [],
                "experience_rewrites": [],
                "project_rewrites": [],
            },
            GeminiAPIException("quota exceeded"),
        ]
    )
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-long")
    profile = {
        "full_name": "Ayşe",
        "work_experiences": [{"title": "Dev", "company": "Y", "description": "uzun açıklama"}],
    }

    with patch("app.agents.cv_generation._pdf_page_count", return_value=2):
        pdf_bytes = await agent.generate(profile, {"position_title": "Dev"})

    assert pdf_bytes == b"%PDF-long"
    # filter + shorten fail → prune loop still tries max_projects 2,1,0 with same profile
    assert agent._compile_with_tectonic.await_count >= 1


@pytest.mark.asyncio
async def test_overflow_recompile_failure_falls_back_to_original_pdf():
    """Kısaltma başarılı ama yeniden derleme kırılırsa yine orijinal PDF dönmeli"""
    fake_client = FakeGeminiClient()
    fake_client.generate_json = AsyncMock(
        side_effect=[
            {
                "experience_indices": [0],
                "project_indices": [],
                "certificate_indices": [],
                "experience_rewrites": [],
                "project_rewrites": [],
            },
            {
                "experience_rewrites": [{"index": 0, "description": "kısa"}],
                "project_rewrites": [],
            },
        ]
    )
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)

    async def compile_once_then_fail(
        tex_source: str, max_retries: int = 2, avatar_bytes=None
    ) -> bytes:
        if not hasattr(compile_once_then_fail, "n"):
            compile_once_then_fail.n = 0
        compile_once_then_fail.n += 1
        if compile_once_then_fail.n == 1:
            return b"%PDF-long"
        raise CVGenerationException("derleme hatası")

    agent._compile_with_tectonic = AsyncMock(side_effect=compile_once_then_fail)
    profile = {
        "full_name": "Ayşe",
        "work_experiences": [{"title": "Dev", "company": "Y", "description": "uzun açıklama"}],
    }

    with patch("app.agents.cv_generation._pdf_page_count", return_value=2):
        pdf_bytes = await agent.generate(profile, {"position_title": "Dev"})

    assert pdf_bytes == b"%PDF-long"


@pytest.mark.asyncio
async def test_overflow_prunes_projects_when_shorten_still_multi_page():
    """Kısaltma sonrası hâlâ >1 sayfa ise proje kotası düşürülerek yeniden derlenmeli"""
    fake_client = FakeGeminiClient()
    fake_client.generate_json = AsyncMock(
        side_effect=[
            {
                "experience_indices": [],
                "project_indices": [0, 1, 2],
                "certificate_indices": [],
                "experience_rewrites": [],
                "project_rewrites": [],
            },
            {
                "experience_rewrites": [],
                "project_rewrites": [
                    {"index": 0, "description": "kısa A"},
                    {"index": 1, "description": "kısa B"},
                    {"index": 2, "description": "kısa C"},
                ],
            },
        ]
    )
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    # 1) ilk derleme 2) kısaltılmış (hâlâ 2 sayfa) 3) max_projects=2 → 1 sayfa
    agent._compile_with_tectonic = AsyncMock(
        side_effect=[b"%PDF-long", b"%PDF-shortened", b"%PDF-pruned"]
    )
    profile = {
        "full_name": "Ayşe",
        "projects": [
            {"title": "A", "description": "uzun A", "tech_stack": ["Python"]},
            {"title": "B", "description": "uzun B", "tech_stack": ["Python"]},
            {"title": "C", "description": "uzun C", "tech_stack": ["Go"]},
        ],
    }

    def page_count(pdf: bytes) -> int:
        return 1 if pdf == b"%PDF-pruned" else 2

    with patch("app.agents.cv_generation._pdf_page_count", side_effect=page_count):
        pdf_bytes = await agent.generate(
            profile, {"position_title": "Backend", "required_skills": ["Python"]}
        )

    assert pdf_bytes == b"%PDF-pruned"
    assert agent._compile_with_tectonic.await_count == 3
    pruned_tex = agent._compile_with_tectonic.call_args_list[2][0][0]
    assert "kısa A" in pruned_tex
    assert "kısa B" in pruned_tex
    # max_projects=2 ve ranking Python'u öne alır → Go projesi düşer
    assert "kısa C" not in pruned_tex


@pytest.mark.asyncio
async def test_overflow_with_no_filterable_content_skips_shorten_call():
    """Deneyim/proje hiç yoksa kısaltma için Gemini'ye gidilmemeli; sertifika filtresi
    çalışır. Prune döngüsü proje kotasını düşürerek yeniden derleyebilir."""
    fake_client = FakeGeminiClient()
    agent = CVGenerationAgent(storage=MagicMock(), client=fake_client)
    agent._compile_with_tectonic = AsyncMock(return_value=b"%PDF-fake")
    profile = {"full_name": "Ayşe", "certificates": [{"title": "X", "issuer": "Y"}]}

    with patch("app.agents.cv_generation._pdf_page_count", return_value=2):
        pdf_bytes = await agent.generate(profile, {"position_title": "Dev"})

    assert pdf_bytes == b"%PDF-fake"
    assert fake_client.generate_json.await_count == 1


@pytest.mark.asyncio
async def test_render_latex_includes_exams():
    agent = CVGenerationAgent(storage=MagicMock())
    tex = agent._render_latex(
        {
            "full_name": "Ayşe",
            "exams": [
                {
                    "name": "YDS",
                    "score": "85",
                    "exam_date": "2024-06-01",
                    "description": "İngilizce",
                }
            ],
        },
        {"position_title": "Dev"},
    )
    assert "YDS" in tex
    assert "85" in tex
    assert "Sınavlar" in tex
