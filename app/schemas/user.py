from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, EmailStr

from app.models.user import User


class UserCreationModel(BaseModel):
    email: EmailStr
    password: str

    full_name: str | None = None


class UserResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4

    email: str
    full_name: str | None

    is_active: bool
    roles: list[str]

    created_at: datetime
    updated_at: datetime


def to_user_response(user: User) -> UserResponseModel:
    return UserResponseModel.model_validate(user)


class UserUpdateModel(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None
    roles: list[str] | None = None
