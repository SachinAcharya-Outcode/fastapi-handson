"""SQLAlchemy engine, session factory, and ``get_db`` dependency.

Use ``DbSessionDep`` as an ``Annotated`` type alias in FastAPI routes
and services to inject a scoped ORM session.
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

__all__ = [
    "DbSessionDep",
    "Session",
    "SessionLocal",
    "engine",
    "get_db",
]

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a scoped SQLAlchemy session; roll back on unhandled errors.

    The session is always closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


DbSessionDep = Annotated[Session, Depends(get_db)]
"""Injectable dependency that yields a scoped SQLAlchemy ORM session.

The session is automatically closed (and rolled back on error) after
the request completes.  Use this in all endpoints and services that
need to query the database.
"""
