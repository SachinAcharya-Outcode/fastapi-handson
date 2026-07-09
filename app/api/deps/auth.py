"""Auth-related dependency injection helpers and type aliases.

Provides reusable dependencies for:
  - Getting the current authenticated user (bearer token)
  - Providing an AuthService instance
"""

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

if TYPE_CHECKING:
    from pydantic import UUID4

from app.db.models import User
from app.db.session import DbSessionDep
from app.exceptions.exceptions import InvalidTokenError
from app.services.auth import AuthService

security = HTTPBearer(auto_error=False)


def get_current_user(
    db: DbSessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> User:
    """Validate the Bearer token and return the authenticated user.

    Raises ``InvalidTokenError`` (401) if the token is missing, expired,
    or does not reference an existing user.
    """
    if credentials is None:
        raise InvalidTokenError("Missing or invalid authorization header")
    token = credentials.credentials
    payload = AuthService.decode_access_token(token)
    user_id: UUID4 | None = payload.get("sub")
    if user_id is None:
        raise InvalidTokenError("Invalid token payload")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise InvalidTokenError("User not found")
    return user


def get_auth_service(db: DbSessionDep) -> AuthService:
    """Provide an AuthService wired with the current DB session."""
    return AuthService(db)


# Annotated type aliases for dependency injection

CurrentUserDep = Annotated[User, Depends(get_current_user)]
"""Injectable dependency that resolves to the currently authenticated user.

Extracts and validates the Bearer token from the ``Authorization`` header,
then returns the matching ``User`` ORM instance.  Raises ``InvalidTokenError``
(401) on missing, expired, or invalid tokens.
"""

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
"""Injectable dependency that provides an ``AuthService`` instance.

The service is wired with the current DB session and exposes
``register``, ``login``, and ``refresh`` operations.
"""
