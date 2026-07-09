"""Base exception class for all application-level errors.

All custom exceptions inherit from ``AppError`` (which extends
``HTTPException``) so that FastAPI handles them natively.  The global
exception handler customises the response shape.
"""

from fastapi import HTTPException


class AppError(HTTPException):
    """Base exception for domain errors across the application.

    Attributes:
        name: Machine-readable error identifier (e.g. ``"USER_NOT_FOUND"``).
        detail: Human-readable description of the error.
        status_code: HTTP status code to return to the client.
    """

    def __init__(self, name: str, detail: str, status_code: int = 400) -> None:
        self.name = name
        self.detail = detail
        self.status_code = status_code
        super().__init__(status_code=status_code, detail=detail)
