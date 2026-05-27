from app.models.base import Base


class Product(Base):
    label: str
    rate: int
    quantity: int
