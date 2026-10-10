"""JSON persistence layer."""
import json
import os
from typing import List

from .models import Product


class StorageError(Exception):
    pass


def load_products(path: str) -> List[Product]:
    """Load products from a JSON file. Returns [] if the file does not exist."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [Product.from_dict(item) for item in raw]
    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
        raise StorageError(f"Data file is corrupted: {exc}") from exc
    except OSError as exc:
        raise StorageError(f"Cannot read data file: {exc}") from exc


def save_products(path: str, products: List[Product]) -> None:
    """Write products to a JSON file (atomic replace)."""
    tmp = path + ".tmp"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in products], f, indent=2)
        os.replace(tmp, path)
    except OSError as exc:
        raise StorageError(f"Cannot save data file: {exc}") from exc
