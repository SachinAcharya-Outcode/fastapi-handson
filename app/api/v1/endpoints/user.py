"""User CRUD endpoints — create, read, update, delete, and list users.

All business logic is delegated to UserService.  Endpoints only map
HTTP request components to service calls and return responses.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page, Params
from pydantic import UUID4

from app.api.deps.auth import CurrentUserDep
from app.api.deps.user import UserServiceDep
from app.db.models import User as UserModel
from app.schemas.user import UserCreationModel, UserResponseModel, UserUpdateModel

router = APIRouter()

# Query-parameter type aliases

SearchQuery = Annotated[str | None, Query(description="Search by email or name")]
"""Optional query parameter for case-insensitive text search across email and name."""

IsActiveQuery = Annotated[bool | None, Query()]
"""Optional query parameter to filter users by their ``is_active`` status."""

SortByQuery = Annotated[str, Query(pattern=r"^(created_at|email|full_name)$")]
"""Column name to sort results by (``created_at``, ``email``, or ``full_name``)."""

SortOrderQuery = Annotated[str, Query(pattern=r"^(asc|desc)$")]
"""Sort direction — ``asc`` or ``desc`` (defaults to ``desc`` in the endpoint)."""

PaginationParams = Annotated[Params, Depends(Params)]
"""Standard fastapi-pagination query parameters (``page`` and ``size``)."""


@router.get("/me", response_model=UserResponseModel)
def get_me(current_user: CurrentUserDep) -> UserModel:
    """Return the authenticated user's profile.

    Requires a valid Bearer token in the Authorization header.
    """
    return current_user


@router.post("/", response_model=UserResponseModel)
def create_user(
    payload: UserCreationModel,
    service: UserServiceDep,
) -> UserModel:
    """Register a new user.

    Raises ``EmailAlreadyExistsError`` (400) if the email is taken.
    """
    return service.create_user(payload)


@router.get("/", response_model=Page[UserResponseModel])
def list_users(
    service: UserServiceDep,
    params: PaginationParams,
    search: SearchQuery = None,
    is_active: IsActiveQuery = None,
    sort_by: SortByQuery = "created_at",
    sort_order: SortOrderQuery = "desc",
) -> Page[UserModel]:
    """List users with optional filtering, sorting, and pagination.

    Query parameters:
      - **search**: filter by email or name (case-insensitive contains)
      - **is_active**: ``true`` / ``false`` to filter by active status
      - **sort_by**: ``created_at`` (default), ``email``, or ``full_name``
      - **sort_order**: ``asc`` or ``desc`` (default)
      - **page** / **size**: standard fastapi-pagination params
    """
    return service.list_users(
        params=params,
        search=search,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{user_id}", response_model=UserResponseModel)
def retrieve_user(
    user_id: UUID4,
    service: UserServiceDep,
) -> UserModel:
    """Get a single user by UUID.

    Raises ``UserNotFoundError`` (404) if the id does not exist.
    """
    return service.retrieve_user(user_id)


@router.patch("/{user_id}", response_model=UserResponseModel)
def update_user(
    user_id: UUID4,
    payload: UserUpdateModel,
    service: UserServiceDep,
) -> UserModel:
    """Partially update a user — only supplied fields are changed.

    Raises ``UserNotFoundError`` (404) if the id does not exist.
    """
    return service.update_user(user_id, payload)


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID4,
    service: UserServiceDep,
) -> dict[str, str]:
    """Delete a user by UUID.

    Raises ``UserNotFoundError`` (404) if the id does not exist.
    """
    service.delete_user(user_id)
    return {"message": "success"}
