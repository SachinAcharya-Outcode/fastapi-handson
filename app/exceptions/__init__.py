"""Application exception hierarchy — re-exported for convenience."""

from app.exceptions.base import AppError
from app.exceptions.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserNotFoundError,
)

__all__ = [
    "AppError",
    "EmailAlreadyExistsError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "UserNotFoundError",
]
