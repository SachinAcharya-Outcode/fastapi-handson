from datetime import UTC, datetime

from pydantic import EmailStr, Field

from app.models.base import Base


class User(Base):
    email: EmailStr
    full_name: str | None = Field(None, max_length=100)
    password: str = Field(..., min_length=8)

    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    roles: list[str] = Field(default_factory=lambda: ["user"])
