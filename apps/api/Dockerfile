FROM --platform=linux/amd64 python:3.11-slim-trixie as builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Tectonic'in resmi Linux binary'leri glibc >= 2.38 ister (bookworm'de 2.36 var, Apple
# Silicon'da arm64 binary hiç yok) - bu yüzden hem builder hem final stage amd64
# (emülasyon) + trixie (glibc 2.39+) tabanlı. CV Ajanı bu image'i kullanır.
FROM --platform=linux/amd64 debian:trixie-slim as tectonic

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates libgraphite2-3 libharfbuzz0b libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*
RUN curl --proto '=https' -tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh \
    && mv tectonic /usr/local/bin/tectonic

FROM --platform=linux/amd64 python:3.11-slim-trixie

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl libgraphite2-3 libharfbuzz0b libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser

COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --from=tectonic --chown=appuser:appuser /usr/local/bin/tectonic /usr/local/bin/tectonic
COPY --chown=appuser:appuser . .

ENV PATH=/home/appuser/.local/bin:$PATH PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/app
# Tectonic derleme sırasında paket indirir (~/.cache/Tectonic); appuser'ın HOME'u yazılabilir olmalı
ENV HOME=/home/appuser

USER appuser
RUN mkdir -p /home/appuser/.cache

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
