from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_compile_sample():
    tex = (FIXTURES / "sample.tex").read_text(encoding="utf-8")
    response = client.post(
        "/compile",
        files={"file": ("sample.tex", tex, "application/x-tex")},
    )
    assert response.status_code == 200
    assert response.content[:5] == b"%PDF-"


def test_compile_invalid():
    tex = (FIXTURES / "invalid.tex").read_text(encoding="utf-8")
    response = client.post(
        "/compile",
        files={"file": ("invalid.tex", tex, "application/x-tex")},
    )
    assert response.status_code == 422
    assert "stderr" in response.json()["detail"]


def test_compile_with_assets():
    tex = (FIXTURES / "sample.tex").read_text(encoding="utf-8")
    cls = r"\ProvidesClass{article}\LoadClass{article}"
    response = client.post(
        "/compile?main=sample.tex",
        files=[
            ("files", ("sample.tex", tex, "application/x-tex")),
            ("files", ("helper.cls", cls, "text/plain")),
        ],
    )
    assert response.status_code == 200
    assert response.content[:5] == b"%PDF-"


def test_rejects_no_tex():
    response = client.post(
        "/compile",
        files={"file": ("doc.txt", "hello", "text/plain")},
    )
    assert response.status_code == 400
