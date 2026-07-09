"""Pydantic models (request/response schemas) for user CRUD endpoints."""

from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr


class UserCreationModel(BaseModel):
    """Payload for ``POST /api/v1/users`` — create a new user."""

    email: EmailStr
    password: str
    full_name: str


class UserUpdateModel(BaseModel):
    """Payload for ``PATCH /api/v1/users/{id}`` — partial update.

    Every field is optional; only supplied fields are modified.
    """

    email: EmailStr | None = None
    password: str | None = None
    full_name: str | None = None
    is_active: bool | None = None


class UserResponseModel(BaseModel):
    """Public representation of a user returned by the API.

    The ``password_hash`` column is intentionally excluded.
    """

    id: UUID4
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
