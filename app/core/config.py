"""Application configuration via environment variables.

Uses pydantic-settings (BaseSettings) to load values from ``.env``
or the process environment.  Secrets like ``SECRET_KEY`` must be set
externally — no fallback defaults are provided for production secrets.
"""

import json
from typing import Annotated

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import NoDecode


class Settings(BaseSettings):
    """Central settings for the FastAPI application.

    Environment variables are case-insensitive in the dotenv file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "FastAPI Hands-on"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8000

    # CORS
    BACKEND_CORS_ORIGINS: Annotated[list[AnyHttpUrl], NoDecode] = Field(
        default=[AnyHttpUrl("http://localhost:3000")]
    )

    # API prefix
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = (
        "postgresql://fastapi_user:fastapi_pass@localhost:5432/fastapi_db"
    )

    # Authentication / JWT
    # SECRET_KEY must be provided via .env or environment —
    # the empty default allows static checkers to accept `Settings()`
    # while runtime validation rejects an empty value.
    SECRET_KEY: str = Field(default="", min_length=1)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email Configuration (SMTP / MailHog)
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@fastapi-handson.local"

    # Profile picture uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from env var — JSON array or comma-separated.

        Trailing slashes are stripped for consistency.
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip().rstrip("/") for i in v.split(",")]
        if isinstance(v, str):

            parsed = json.loads(v)
            if isinstance(parsed, list):
                return [str(origin).rstrip("/") for origin in parsed]
            raise ValueError(f"Expected a JSON array, got {type(parsed).__name__}")
        if isinstance(v, list):
            return [str(origin).rstrip("/") for origin in v]
        raise ValueError(f"Unexpected type for CORS origins: {type(v).__name__}")


settings = Settings()
