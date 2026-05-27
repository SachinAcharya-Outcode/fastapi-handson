from pydantic import Field

from app.models.product import Product
from app.models.user import User


class Seller(User):
    products: list[Product] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=lambda: ["user", "seller"])
