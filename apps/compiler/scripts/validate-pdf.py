#!/usr/bin/env python3
"""Validate that a file is a readable PDF."""

import sys
from pathlib import Path

from pypdf import PdfReader


def validate(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"File not found: {path}")
    if path.read_bytes()[:5] != b"%PDF-":
        raise SystemExit(f"Not a PDF: {path}")
    reader = PdfReader(str(path))
    if len(reader.pages) < 1:
        raise SystemExit(f"PDF has no pages: {path}")


if __name__ == "__main__":
    validate(Path(sys.argv[1]))
    print(f"OK: {sys.argv[1]}")
