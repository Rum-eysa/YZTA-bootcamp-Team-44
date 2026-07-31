"""Object storage servisi - CV PDF'leri için MinIO (S3-uyumlu, private bucket)"""
import uuid
from functools import lru_cache

import boto3
from app.config import settings
from botocore.client import Config
from botocore.exceptions import ClientError

# Presigned URL ömrü (saniye)
PRESIGNED_EXPIRES_SECONDS = 3600


class StorageService:
    """MinIO/S3 üzerinde CV PDF / avatar depolama (private + presigned)."""

    def __init__(self):
        self.bucket = settings.STORAGE_BUCKET
        self.public_url = settings.STORAGE_PUBLIC_URL.rstrip("/")
        self._client_kwargs = {
            "aws_access_key_id": settings.STORAGE_ACCESS_KEY,
            "aws_secret_access_key": settings.STORAGE_SECRET_KEY,
            "config": Config(signature_version="s3v4"),
            "region_name": "us-east-1",
        }
        # Container içi erişim (upload/download)
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.STORAGE_ENDPOINT,
            **self._client_kwargs,
        )
        # Tarayıcıya verilen imzalı URL'ler public host ile imzalanmalı
        # (aksi halde host=minio:9000 olur; tarayıcı çözemez ve imza bozulur).
        self._presign_client = boto3.client(
            "s3",
            endpoint_url=self.public_url,
            **self._client_kwargs,
        )

    def ensure_bucket(self) -> None:
        """Bucket yoksa oluştur; public okuma politikası uygulanmaz."""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket)
        # Eski public politikayı kaldırmaya çalış (yoksa yok say)
        try:
            self.client.delete_bucket_policy(Bucket=self.bucket)
        except ClientError:
            pass

    def _stable_url(self, key: str) -> str:
        """DB'de saklanan kararlı URL (presigned değil)."""
        return f"{self.public_url}/{self.bucket}/{key}"

    def upload_cv(self, user_id: str, pdf_bytes: bytes) -> str:
        """PDF'i private bucket'a yükler; kararlı storage URL döner."""
        key = f"cv/{user_id}/{uuid.uuid4()}.pdf"
        self.client.put_object(
            Bucket=self.bucket, Key=key, Body=pdf_bytes, ContentType="application/pdf"
        )
        return self._stable_url(key)

    def upload_avatar(self, user_id: str, image_bytes: bytes, content_type: str) -> str:
        """Profil fotoğrafını private bucket'a yükler; kararlı storage URL döner."""
        ext = {
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
        }.get(content_type, "jpg")
        key = f"avatars/{user_id}/{uuid.uuid4()}.{ext}"
        self.client.put_object(
            Bucket=self.bucket, Key=key, Body=image_bytes, ContentType=content_type
        )
        return self._stable_url(key)

    def _object_key_from_url(self, url: str) -> str | None:
        """Public veya internal URL'den bucket key çıkarır."""
        if not url:
            return None
        # Zaten presigned ise query'siz path'ten key çıkar
        url_no_query = url.split("?", 1)[0]
        prefix = f"{self.public_url}/{self.bucket}/"
        if url_no_query.startswith(prefix):
            return url_no_query[len(prefix) :]
        marker = f"/{self.bucket}/"
        if marker in url_no_query:
            return url_no_query.split(marker, 1)[1]
        return None

    def presign_url(
        self, url: str | None, expires_in: int = PRESIGNED_EXPIRES_SECONDS
    ) -> str | None:
        """Kararlı storage URL'ini kısa ömürlü imzalı URL'e çevirir."""
        if not url:
            return None
        # Zaten imzalı görünüyorsa olduğu gibi bırak
        if "X-Amz-Signature=" in url or "X-Amz-Credential=" in url:
            return url
        key = self._object_key_from_url(url)
        if not key:
            return url
        try:
            return self._presign_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except ClientError:
            return url

    def download_bytes(self, url: str) -> bytes | None:
        """Storage URL'den nesneyi S3 API ile indirir; başarısızsa None."""
        key = self._object_key_from_url(url)
        if not key:
            return None
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=key)
            return obj["Body"].read()
        except ClientError:
            return None


@lru_cache
def get_storage_service() -> StorageService:
    return StorageService()
