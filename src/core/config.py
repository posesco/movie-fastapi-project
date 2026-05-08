from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # Project
    project_title: str = Field(default="Fast API", validation_alias="PROJECT_TITLE")
    project_version: str = Field(default="1.2.1", validation_alias="PROJECT_VERSION")
    project_desc: str = Field(default="API built with FastAPI", validation_alias="PROJECT_DESC")
    project_debug_mode: bool = Field(default=False, validation_alias="PROJECT_DEBUG_MODE")

    # Admin
    admin_name: str = Field(default="admin", validation_alias="ADMIN_NAME")
    admin_surname: str = Field(default="admin", validation_alias="ADMIN_SURNAME")
    admin_user: str = Field(default="admin", validation_alias="ADMIN_USER")
    admin_email: str = Field(default="admin@example.com", validation_alias="ADMIN_EMAIL")
    admin_pass: str = Field(default="admin", validation_alias="ADMIN_PASS", repr=False)

    # Auth
    secret_key: str = Field(default="secret", validation_alias="SECRET_KEY", repr=False)
    algorithm: str = Field(default="HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # PostgreSQL
    postgres_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    postgres_db: str = Field(default="postgres", validation_alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", validation_alias="POSTGRES_PASSWORD", repr=False)

    # OTEL
    otel_collector_endpoint: str = Field(default="http://localhost:4317", validation_alias="OTEL_COLLECTOR_ENDPOINT")
    otel_service_name: str = Field(default="fastapi-app", validation_alias="OTEL_SERVICE_NAME")
    otel_enabled: bool = Field(default=False, validation_alias="OTEL_ENABLED")

    # Redis
    redis_host: str = Field(default="localhost", validation_alias="REDIS_HOST")
    redis_port: int = Field(default=6379, validation_alias="REDIS_PORT")
    redis_db: int = Field(default=0, validation_alias="REDIS_DB")
    redis_password: str | None = Field(default=None, validation_alias="REDIS_PASSWORD", repr=False)

    # S3
    s3_endpoint: str = Field(default="http://localhost:9000", validation_alias="S3_ENDPOINT")
    s3_access_key: str = Field(default="storageadmin", validation_alias="S3_ACCESS_KEY", repr=False)
    s3_secret_key: str = Field(default="storagepassword", validation_alias="S3_SECRET_KEY", repr=False)
    s3_bucket_name: str = Field(default="fastapi-bucket", validation_alias="S3_BUCKET_NAME")
    s3_region: str = Field(default="us-east-1", validation_alias="S3_REGION")
    s3_use_ssl: bool = Field(default=False, validation_alias="S3_USE_SSL")
    s3_public_url: str = Field(default="http://localhost:9000", validation_alias="S3_PUBLIC_URL")

    # Storage
    storage_backend: str = Field(default="s3", validation_alias="STORAGE_BACKEND")
    local_storage_path: str = Field(default="uploads", validation_alias="LOCAL_STORAGE_PATH")

    # Security
    backend_cors_origins: list[str] = Field(default=[], validation_alias="BACKEND_CORS_ORIGINS")
    allowed_hosts: list[str] = Field(
        default=["localhost", "127.0.0.1", "testserver"], 
        validation_alias="ALLOWED_HOSTS"
    )

    # Computed
    @computed_field
    @property
    def redis_url(self) -> str:
        if self.redis_password:
            password = quote_plus(self.redis_password)
            return f"redis://:{password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @computed_field
    @property
    def database_url(self) -> str:
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql://{self.postgres_user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def async_database_url(self) -> str:
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()

tags_metadata = [
    {
        "name": "Users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Movies",
        "description": "Manage movies. You can also **search** and **filter** them.",
    },
    {
        "name": "Upload",
        "description": "Upload files. This can be used for uploading movie posters or other related files.",  
    },
    {
        "name": "health",
        "description": "Well, it's a way to tell if it's alive",
    }
]