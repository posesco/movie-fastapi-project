from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
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
