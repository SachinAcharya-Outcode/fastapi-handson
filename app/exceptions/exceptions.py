from fastapi import status

from app.exceptions.base import AppError


class EmailAlreadyExistsError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__("EMAIL_ALREADY_EXIST", message, status.HTTP_400_BAD_REQUEST)


class UserNotFoundError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__("USER_NOT_FOUND", message, status.HTTP_404_NOT_FOUND)


class BadRequestError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__("BAD_REQUEST", message, status.HTTP_400_BAD_REQUEST)
