"""User CRUD service — create, read, update, delete, and list users.

All database queries live here so endpoints stay free of ORM imports.
"""

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import UUID4
from sqlalchemy import desc as sa_desc

from app.db.models import User
from app.db.session import Session
from app.exceptions.exceptions import EmailAlreadyExistsError, UserNotFoundError
from app.schemas.user import UserCreationModel, UserUpdateModel
from app.services.auth import hash_password


class UserService:
    """High-level user operations executed inside a DB session."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_user(self, payload: UserCreationModel) -> User:
        """Insert a new user after checking for email uniqueness.

        Raises ``EmailAlreadyExistsError`` (400) when the email is taken.
        """
        existing = self.db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise EmailAlreadyExistsError()

        user = User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def retrieve_user(self, user_id: UUID4) -> User:
        """Return a single user by id.

        Raises ``UserNotFoundError`` (404) if the id does not exist.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError()
        return user

    def update_user(self, user_id: UUID4, payload: UserUpdateModel) -> User:
        """Apply partial updates to a user.

        Only the fields present (not ``None``) are applied.
        Raises ``UserNotFoundError`` (404) if the id does not exist.
        """
        user = self.retrieve_user(user_id)
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password":
                user.password_hash = hash_password(value)
            else:
                setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: UUID4) -> None:
        """Remove a user by id.

        Raises ``UserNotFoundError`` (404) if the id does not exist.
        """
        user = self.retrieve_user(user_id)
        self.db.delete(user)
        self.db.commit()

    def list_users(
        self,
        params: Params,
        search: str | None = None,
        is_active: bool | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Page[User]:
        """Return a paginated, filterable, sortable list of users.

        Keyword arguments:
          search — case-insensitive substring match on email or name
          is_active — ``True`` / ``False`` to filter by active status
          sort_by — column name (``created_at``, ``email``, ``full_name``)
          sort_order — ``asc`` or ``desc`` (default)
        """
        query = self.db.query(User)

        if search:
            pattern = f"%{search.lower()}%"
            query = query.filter(
                User.email.ilike(pattern) | User.full_name.ilike(pattern)
            )

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        sort_column = getattr(User, sort_by, User.created_at)
        if sort_order == "desc":
            sort_column = sa_desc(sort_column)
        query = query.order_by(sort_column)

        return paginate(query, params)
