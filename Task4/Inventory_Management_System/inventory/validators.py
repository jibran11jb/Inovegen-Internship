"""Input validation helpers. Each returns a clean value or raises ValueError."""


def validate_text(value: str, field: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field} cannot be empty.")
    if len(value) > 60:
        raise ValueError(f"{field} must be 60 characters or fewer.")
    return value


def validate_product_id(value: str) -> str:
    value = value.strip().upper()
    if not value:
        raise ValueError("Product ID cannot be empty.")
    if not value.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Product ID may contain only letters, digits, '-' and '_'.")
    return value


def validate_quantity(value: str, allow_zero: bool = True) -> int:
    try:
        qty = int(str(value).strip())
    except ValueError:
        raise ValueError("Quantity must be a whole number.")
    if qty < 0 or (qty == 0 and not allow_zero):
        raise ValueError("Quantity must be " + ("zero or more." if allow_zero else "greater than zero."))
    return qty


def validate_price(value: str) -> float:
    try:
        price = float(str(value).strip())
    except ValueError:
        raise ValueError("Price must be a number.")
    if price < 0:
        raise ValueError("Price cannot be negative.")
    return round(price, 2)
