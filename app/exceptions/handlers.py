"""FastAPI exception handler for ``AppError`` subclasses."""

from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.base import AppError


async def app_exception_handler(
    _request: Request,
    exc: AppError,
) -> JSONResponse:
    """Catch any ``AppError`` and format it as a JSON error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "name": exc.name,
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )
