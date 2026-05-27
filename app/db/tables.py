from app.db.engine import MockTable
from app.models.product import Product
from app.models.seller import Seller
from app.models.user import User


class Tables:
    def __init__(self) -> None:
        self.users: MockTable[User] = MockTable[User]()
        self.sellers: MockTable[Seller] = MockTable[Seller]()
        self.products: MockTable[Product] = MockTable[Product]()


tables = Tables()
