"""User-service dependency injection helpers and type aliases."""

from typing import Annotated

from fastapi import Depends

from app.db.session import DbSessionDep
from app.services.user import UserService


def get_user_service(db: DbSessionDep) -> UserService:
    """Provide a UserService wired with the current DB session."""
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
"""Injectable dependency that provides a ``UserService`` instance.

The service is wired with the current DB session and exposes
full CRUD operations for the ``User`` model.
"""
