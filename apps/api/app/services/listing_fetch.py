"""İlan URL'sinden metin çıkarma yardımcıları"""
import re

import httpx
from app.exceptions import ValidationException


def _strip_html(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


async def fetch_listing_text_from_url(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "CareerTrackBot/1.0"})
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ValidationException(f"URL içeriği alınamadı: {exc}") from exc

    content_type = response.headers.get("content-type", "")
    if "text/html" in content_type or "<html" in response.text.lower():
        text = _strip_html(response.text)
    else:
        text = response.text.strip()

    if len(text) < 50:
        raise ValidationException("URL'den çıkarılan metin çok kısa (en az 50 karakter gerekli)")

    return text[:20_000]
