from pydantic import UUID4

from app.db.tables import tables
from app.exceptions.exceptions import EmailAlreadyExistsError
from app.models.user import User
from app.schemas.user import UserCreationModel, UserUpdateModel


class UserService:
    def __init__(self) -> None:
        self.table = tables["users"]

    def list_users(self) -> list[User]:
        return self.table.all()

    def retrieve_user(self, pk: UUID4) -> User:
        return self.table.get({"id": pk}, raise_if_missing=True)

    def create_user(self, data: UserCreationModel) -> User:
        if self.table.exists({"email": data.email}):
            raise EmailAlreadyExistsError("User with this email already exists.")

        user = User(email=data.email, full_name=data.full_name, password=data.password)
        self.table.insert(user)
        return user

    def update_user(self, pk: UUID4, data: UserUpdateModel) -> User | None:
        update_data: dict[str, str | bool | list[str]] = {}

        if data.full_name is not None:
            update_data["full_name"] = data.full_name

        if data.is_active is not None:
            update_data["is_active"] = data.is_active

        if data.roles is not None:
            update_data["roles"] = data.roles

        if not update_data:
            # nothing to update, just return existing user
            return self.table.get({"id": pk})

        user = self.table.update_by(
            {"id": pk},
            update_data,
            raise_if_missing=True,
        )

        user.touch()

        return user

    def delete_user(self, pk: UUID4) -> None:
        self.table.delete_by({"id": pk}, raise_if_missing=True)
