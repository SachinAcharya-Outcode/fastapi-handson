from typing import TypedDict

from app.db.engine import MockTable
from app.models.product import Product
from app.models.seller import Seller
from app.models.user import User


# Database Tables
class TableSchema(TypedDict):
    users: MockTable[User]
    sellers: MockTable[Seller]
    products: MockTable[Product]


tables: TableSchema = {
    "users": MockTable[User](),
    "sellers": MockTable[Seller](),
    "products": MockTable[Product](),
}
