"""CareerTrack tarafından üretilen PDF'leri işaretleme / tanıma."""
from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

CAREERTRACK_PRODUCER = "CareerTrack"
CAREERTRACK_CREATOR = "CareerTrack ATS CV"


def stamp_careertrack_pdf(pdf_bytes: bytes) -> bytes:
    """Üretilen CV PDF'ine CareerTrack metadata damgası ekler."""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
    except PdfReadError:
        return pdf_bytes

    writer = PdfWriter()
    writer.append(reader)
    writer.add_metadata(
        {
            "/Producer": CAREERTRACK_PRODUCER,
            "/Creator": CAREERTRACK_CREATOR,
        }
    )
    out = BytesIO()
    writer.write(out)
    return out.getvalue()


def is_careertrack_pdf(pdf_bytes: bytes) -> bool:
    """PDF metadata'sında CareerTrack damgası var mı?"""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
    except Exception:  # noqa: BLE001
        return False
    meta = reader.metadata
    if not meta:
        return False
    blob = " ".join(
        str(meta.get(key) or "") for key in ("/Producer", "/Creator", "/Title", "/Author")
    )
    return "CareerTrack" in blob
