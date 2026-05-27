from pydantic import ConfigDict, Field

from app.models.product import Product
from app.models.seller import Seller
from app.schemas.user import UserCreationModel


class SellerCreationModel(UserCreationModel):
    products: list[Product] = Field(default_factory=list)


class SellerResponseModel(Seller):
    model_config = ConfigDict(from_attributes=True)
