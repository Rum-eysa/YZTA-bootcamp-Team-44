"""Application settings - environment degiskenlerinden okunur"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    LOG_LEVEL: str = "debug"

    DATABASE_URL: str = "postgresql://yzta_user:yzta_password@localhost:5432/yzta_bootcamp"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET: str = "change-me-in-production-min-32-characters"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-latest"

    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    # API'nin kendi domain'leri (staging/prod'da TrustedHost için; virgülle ayrık).
    # CORS_ORIGINS frontend origin'leridir - API'nin Railway domain'ini kapsamaz.
    ALLOWED_HOSTS: str = ""

    STORAGE_ENDPOINT: str = "http://localhost:9000"
    STORAGE_ACCESS_KEY: str = "yzta_minio"
    STORAGE_SECRET_KEY: str = "yzta_minio_password"
    STORAGE_BUCKET: str = "cv-documents"
    STORAGE_PUBLIC_URL: str = "http://localhost:9000"

    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.0


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
