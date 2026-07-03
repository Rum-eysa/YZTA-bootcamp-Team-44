FROM debian:bookworm-slim AS tectonic

ARG TARGETARCH
ARG TECTONIC_VERSION=0.16.9

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && case "${TARGETARCH}" in \
         amd64) TECTONIC_ARCH=x86_64-unknown-linux-gnu ;; \
         arm64) TECTONIC_ARCH=aarch64-unknown-linux-musl ;; \
         *) echo "Unsupported arch: ${TARGETARCH}" && exit 1 ;; \
       esac \
    && curl -fsSL -o /tmp/tectonic.tar.gz \
       "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40${TECTONIC_VERSION}/tectonic-${TECTONIC_VERSION}-${TECTONIC_ARCH}.tar.gz" \
    && tar -xzf /tmp/tectonic.tar.gz -C /usr/local/bin \
    && rm -rf /var/lib/apt/lists/* /tmp/tectonic.tar.gz

FROM python:3.11-slim

COPY --from=tectonic /usr/local/bin/tectonic /usr/local/bin/tectonic

ENV TECTONIC_CACHE_DIR=/cache \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl fontconfig \
        fonts-lato fonts-roboto fonts-roboto-slab \
        texlive-xetex texlive-latex-extra texlive-fonts-extra \
        texlive-bibtex-extra biber \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 compiler

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY fixtures/ ./fixtures/
COPY scripts/ ./scripts/
RUN chmod +x scripts/smoke-test.sh

RUN mkdir -p /cache /tmp/prime \
    && tectonic fixtures/sample.tex --outdir /tmp/prime \
    && rm /tmp/prime/sample.pdf

RUN chown -R compiler:compiler /app /cache

USER compiler

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
