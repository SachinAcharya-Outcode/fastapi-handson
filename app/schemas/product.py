from pydantic import BaseModel, ConfigDict

from app.models.product import Product


class ProductCreationModel(BaseModel):
    label: str
    rate: int
    quantity: int


class ProductResponseModel(Product):
    model_config = ConfigDict(from_attributes=True)
