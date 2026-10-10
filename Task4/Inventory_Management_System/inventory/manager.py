"""Business logic: the Inventory class."""
from typing import List, Optional

from .models import Product
from . import storage


class InventoryError(Exception):
    pass


class Inventory:
    def __init__(self, path: str):
        self.path = path
        self.products: List[Product] = storage.load_products(path)

    def _save(self) -> None:
        storage.save_products(self.path, self.products)

    def get(self, product_id: str) -> Optional[Product]:
        return next((p for p in self.products if p.product_id == product_id), None)

    def _require(self, product_id: str) -> Product:
        product = self.get(product_id)
        if product is None:
            raise InventoryError(f"No product found with ID '{product_id}'.")
        return product

    def add(self, product: Product) -> None:
        if self.get(product.product_id):
            raise InventoryError(f"Product ID '{product.product_id}' already exists.")
        self.products.append(product)
        self._save()

    def search(self, term: str) -> List[Product]:
        term = term.strip().lower()
        return [
            p for p in self.products
            if term in p.product_id.lower() or term in p.name.lower() or term in p.category.lower()
        ]

    def update(self, product_id: str, name=None, category=None, quantity=None, price=None) -> Product:
        p = self._require(product_id)
        if name is not None:
            p.name = name
        if category is not None:
            p.category = category
        if quantity is not None:
            p.quantity = quantity
        if price is not None:
            p.price = price
        self._save()
        return p

    def delete(self, product_id: str) -> Product:
        p = self._require(product_id)
        self.products.remove(p)
        self._save()
        return p

    def stock_in(self, product_id: str, amount: int) -> Product:
        if amount <= 0:
            raise InventoryError("Stock-in amount must be greater than zero.")
        p = self._require(product_id)
        p.quantity += amount
        self._save()
        return p

    def stock_out(self, product_id: str, amount: int) -> Product:
        if amount <= 0:
            raise InventoryError("Stock-out amount must be greater than zero.")
        p = self._require(product_id)
        if amount > p.quantity:
            raise InventoryError(f"Insufficient stock: only {p.quantity} unit(s) of '{p.name}' available.")
        p.quantity -= amount
        self._save()
        return p

    def total_value(self) -> float:
        return sum(p.total_value for p in self.products)

    def low_stock(self, threshold: int = 10) -> List[Product]:
        return [p for p in self.products if p.quantity <= threshold]
