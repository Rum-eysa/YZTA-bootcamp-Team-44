"""CV Ajanı testleri: LaTeX escape güvenliği + retry mantığı (mock subprocess/Tectonic yok)"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.agents.cv_generation import (
    CVGenerationAgent,
    CVGenerationException,
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
