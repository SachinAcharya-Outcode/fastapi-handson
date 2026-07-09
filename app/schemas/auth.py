"""Pydantic models (request/response schemas) for authentication endpoints."""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Payload for ``POST /auth/register``."""

    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    """Payload for ``POST /auth/login``."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Payload for ``POST /auth/refresh``."""

    refresh_token: str


class RegisterResponse(BaseModel):
    """Response returned on successful registration."""

    email: str
    full_name: str
    message: str = "Registration successful. Please log in."


class TokenResponse(BaseModel):
    """Response returned on successful login or refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105
