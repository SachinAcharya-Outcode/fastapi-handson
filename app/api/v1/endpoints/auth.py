"""Authentication endpoints — register, login, token refresh, and logout.

Each endpoint delegates all business logic to AuthService and returns
the response model directly.  No DB queries or token generation happen here.
"""

from fastapi import APIRouter

from app.api.deps.auth import AuthServiceDep
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)

router = APIRouter()


@router.post("/register")
def register(
    payload: RegisterRequest,
    service: AuthServiceDep,
) -> RegisterResponse:
    """Create a new user account.

    The user must call ``/login`` to obtain access and refresh tokens.

    Raises ``EmailAlreadyExistsError`` (400) if the email is taken.
    """
    return service.register(payload)


@router.post("/login")
def login(
    payload: LoginRequest,
    service: AuthServiceDep,
) -> TokenResponse:
    """Authenticate with email/password and return access + refresh tokens.

    Raises ``InvalidCredentialsError`` (401) on bad credentials.
    """
    return service.login(payload)


@router.post("/refresh")
def refresh(
    payload: RefreshRequest,
    service: AuthServiceDep,
) -> TokenResponse:
    """Issue a new token pair using a valid refresh token.

    Raises ``InvalidTokenError`` (401) if the refresh token is expired,
    malformed, or does not belong to an existing user.
    """
    return service.refresh(payload)


@router.post("/logout")
def logout() -> dict[str, str]:
    """Acknowledge logout.

    In this stateless JWT setup the client is expected to discard its
    tokens.  Server-side blacklisting can be added later if needed.
    """
    return {"message": "Logged out successfully"}
