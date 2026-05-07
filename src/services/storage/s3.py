import aioboto3
from .base import StorageProvider
from src.core.config import settings

class S3StorageProvider(StorageProvider):
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket_name = settings.s3_bucket_name
        self.endpoint_url = settings.s3_endpoint
        self.access_key = settings.s3_access_key
        self.secret_key = settings.s3_secret_key
        self.region_name = settings.s3_region
        self.use_ssl = settings.s3_use_ssl
        self.public_url = settings.s3_public_url

    async def upload_file(
        self, 
        file_bytes: bytes, 
        key: str, 
        content_type: str
    ) -> str:
        async with self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name,
            use_ssl=self.use_ssl,
        ) as s3:
            await s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_bytes,
                ContentType=content_type
            )
        return f"{self.public_url}/{self.bucket_name}/{key}"

    async def delete_file(self, key: str) -> None:
        async with self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name,
            use_ssl=self.use_ssl,
        ) as s3:
            await s3.delete_object(Bucket=self.bucket_name, Key=key)
