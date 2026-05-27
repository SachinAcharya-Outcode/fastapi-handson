from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Project Settings
    PROJECT_NAME: str = "FastAPI Project"
    API_V1_STR: str = "/api/v1"

    PORT: int = 8000
    DEBUG: bool = False

    # Supports CSV or JSON list
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip().rstrip("/") for i in v.split(",")]
        if isinstance(v, list):
            return [str(origin).rstrip("/") for origin in v]
        if isinstance(v, str):
            return v
        raise ValueError(v)


settings = Settings()
