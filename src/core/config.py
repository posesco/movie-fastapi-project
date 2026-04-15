from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    project_title: str = "Movie API"
    project_version: str = "0.0.1"
    project_desc: str = "Movie API with FastAPI"
    project_debug_mode: bool = True
    admin_user: str = "admin"
    admin_email: str = "admin@example.com"
    admin_pass: str = "admin"
    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    database_url: Optional[str] = None
    async_database_url: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="allow",
    )


settings = Settings()

tags_metadata = [
    {
        "name": "Users",
        "description": "Operations with users. The **login** logic is also here.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://posesco.com/users",
        },
    },
    {
        "name": "Movies",
        "description": "Manage movies. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Movies external docs",
            "url": "https://posesco.com/movies",
        },
    },
]
