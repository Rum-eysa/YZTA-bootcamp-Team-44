"""İlan URL'sinden metin çıkarma yardımcıları (SSRF korumalı)"""
import ipaddress
import re
import socket
from urllib.parse import urljoin, urlparse

import httpx
from app.exceptions import ValidationException

_MAX_REDIRECTS = 3
_BLOCKED_HOSTS = frozenset(
    {
        "localhost",
        "metadata.google.internal",
        "metadata",
    }
)


def _strip_html(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _assert_safe_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValidationException("Yalnızca http/https URL'leri desteklenir")
    host = (parsed.hostname or "").strip().lower()
    if not host:
        raise ValidationException("Geçersiz URL")
    if host in _BLOCKED_HOSTS or host.endswith(".local") or host.endswith(".internal"):
        raise ValidationException("Bu URL'ye erişime izin verilmiyor")
    try:
        ip = ipaddress.ip_address(host)
        if _is_blocked_ip(ip):
            raise ValidationException("Bu URL'ye erişime izin verilmiyor")
        return
    except ValueError:
        pass
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ValidationException(f"URL içeriği alınamadı: {exc}") from exc
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except (ValueError, IndexError):
            continue
        if _is_blocked_ip(ip):
            raise ValidationException("Bu URL'ye erişime izin verilmiyor")


async def fetch_listing_text_from_url(url: str) -> str:
    _assert_safe_url(url)
    current = url
    response: httpx.Response | None = None
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
            for _ in range(_MAX_REDIRECTS + 1):
                _assert_safe_url(current)
                response = await client.get(current, headers={"User-Agent": "CareerTrackBot/1.0"})
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        raise ValidationException("URL içeriği alınamadı: redirect hedefi yok")
                    current = urljoin(str(response.url), location)
                    continue
                response.raise_for_status()
                break
            else:
                raise ValidationException("URL içeriği alınamadı: çok fazla yönlendirme")
    except httpx.HTTPError as exc:
        raise ValidationException(f"URL içeriği alınamadı: {exc}") from exc

    assert response is not None
    content_type = response.headers.get("content-type", "")
    if "text/html" in content_type or "<html" in response.text.lower():
        text = _strip_html(response.text)
    else:
        text = response.text.strip()

    if len(text) < 50:
        raise ValidationException("URL'den çıkarılan metin çok kısa (en az 50 karakter gerekli)")

    return text[:20_000]
