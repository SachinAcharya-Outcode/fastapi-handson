"""Health-check endpoint for monitoring/liveness probes.

Returns a detailed status report including database connectivity.
Returns HTTP 503 when the database is unreachable.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.db.session import DbSessionDep

router = APIRouter()


@router.get("/")
async def health_check(db: DbSessionDep) -> JSONResponse:
    """Return backend and database health status.

    Checks:
      - **database**: executes ``SELECT 1`` to verify the connection
    """
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    status = "healthy" if db_ok else "unhealthy"
    status_code = 200 if db_ok else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "version": settings.VERSION,
            "database": "connected" if db_ok else "disconnected",
        },
    )
