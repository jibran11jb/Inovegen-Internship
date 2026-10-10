"""Data model for a single inventory product."""
from dataclasses import dataclass, asdict


@dataclass
class Product:
    product_id: str
    name: str
    category: str
    quantity: int
    price: float

    @property
    def total_value(self) -> float:
        return self.quantity * self.price

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        return cls(
            product_id=str(data["product_id"]),
            name=str(data["name"]),
            category=str(data["category"]),
            quantity=int(data["quantity"]),
            price=float(data["price"]),
        )
