"""Object storage servisi - CV PDF'leri için MinIO (S3-uyumlu)"""
import uuid
from functools import lru_cache

import boto3
from app.config import settings
from botocore.client import Config
from botocore.exceptions import ClientError


class StorageService:
    """MinIO/S3 üzerinde CV PDF depolama"""

    def __init__(self):
        self.bucket = settings.STORAGE_BUCKET
        self.public_url = settings.STORAGE_PUBLIC_URL.rstrip("/")
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.STORAGE_ENDPOINT,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

    def ensure_bucket(self) -> None:
        """Bucket yoksa oluştur ve herkese açık okumaya izin ver (CV indirme linki için)"""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket)
            self.client.put_bucket_policy(
                Bucket=self.bucket,
                Policy=(
                    '{"Version":"2012-10-17","Statement":[{"Effect":"Allow",'
                    '"Principal":"*","Action":"s3:GetObject",'
                    f'"Resource":"arn:aws:s3:::{self.bucket}/*"}}]}}'
                ),
            )

    def upload_cv(self, user_id: str, pdf_bytes: bytes) -> str:
        """PDF'i yükler, herkese açık indirilebilir URL döner"""
        key = f"cv/{user_id}/{uuid.uuid4()}.pdf"
        self.client.put_object(
            Bucket=self.bucket, Key=key, Body=pdf_bytes, ContentType="application/pdf"
        )
        return f"{self.public_url}/{self.bucket}/{key}"


@lru_cache
def get_storage_service() -> StorageService:
    return StorageService()
