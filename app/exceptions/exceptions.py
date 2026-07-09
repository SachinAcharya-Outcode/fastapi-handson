"""Concrete application exception classes mapped to HTTP status codes."""

from fastapi import status

from app.exceptions.base import AppError


class EmailAlreadyExistsError(AppError):
    """Raised when attempting to register with a duplicate email (400)."""

    def __init__(self) -> None:
        super().__init__(
            name="EMAIL_ALREADY_EXISTS",
            detail="Email already registered",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidCredentialsError(AppError):
    """Raised on incorrect email/password login attempt (401)."""

    def __init__(self) -> None:
        super().__init__(
            name="INVALID_CREDENTIALS",
            detail="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidTokenError(AppError):
    """Raised when a JWT is missing, expired, or malformed (401)."""

    def __init__(self, detail: str = "Invalid or expired token") -> None:
        super().__init__(
            name="INVALID_TOKEN",
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class UserNotFoundError(AppError):
    """Raised when a user UUID does not match any record (404)."""

    def __init__(self) -> None:
        super().__init__(
            name="USER_NOT_FOUND",
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
