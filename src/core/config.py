from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # Project
    project_title: str = Field(default="Fast API", validation_alias="PROJECT_TITLE")
    project_version: str = Field(default="0.1.0", validation_alias="PROJECT_VERSION")
    project_desc: str = Field(default="API built with FastAPI", validation_alias="PROJECT_DESC")
    project_debug_mode: bool = Field(default=True, validation_alias="PROJECT_DEBUG_MODE")

    # Admin
    admin_user: str = Field(default="admin", validation_alias="ADMIN_USER")
    admin_email: str = Field(default="admin@example.com", validation_alias="ADMIN_EMAIL")
    admin_pass: str = Field(default="admin", validation_alias="ADMIN_PASS", repr=False)

    # Auth
    secret_key: str = Field(default="secret", validation_alias="SECRET_KEY", repr=False)
    algorithm: str = Field(default="HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # PostgreSQL
    postgres_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    postgres_db: str = Field(default="postgres", validation_alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", validation_alias="POSTGRES_PASSWORD", repr=False)

    # OTEL
    otel_collector_endpoint: str = Field(default="http://alloy:4317", validation_alias="OTEL_COLLECTOR_ENDPOINT")
    otel_service_name: str = Field(default="fastapi-app", validation_alias="OTEL_SERVICE_NAME")
    otel_enabled: bool = Field(default=False, validation_alias="OTEL_ENABLED")
    # Runtime
    running_in_docker: bool = Field(default=False, validation_alias="RUNNING_IN_DOCKER")

    # Computed
    @computed_field
    @property
    def effective_postgres_host(self) -> str:
        return "postgres" if self.running_in_docker else self.postgres_host

    @computed_field
    @property
    def database_url(self) -> str:
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql://{self.postgres_user}:{password}"
            f"@{self.effective_postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def async_database_url(self) -> str:
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{password}"
            f"@{self.effective_postgres_host}:{self.postgres_port}/{self.postgres_db}"
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
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://jesusposada.website/users",
        },
    },
    {
        "name": "Movies",
        "description": "Manage movies. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Movies external docs",
            "url": "https://jesusposada.website/movies",
        },
    },
]