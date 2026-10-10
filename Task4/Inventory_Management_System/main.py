"""Inventory Management System - CLI entry point."""
import os
import sys
from typing import List

from inventory.manager import Inventory, InventoryError
from inventory.models import Product
from inventory.storage import StorageError
from inventory import validators as v

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "inventory.json")
LOW_STOCK_THRESHOLD = 10

MENU = """
==============================
   INVENTORY MANAGEMENT SYSTEM
==============================
 1. Add product
 2. View all products
 3. Search products
 4. Update product
 5. Delete product
 6. Stock in
 7. Stock out
 8. Total inventory value
 9. Low-stock report
 0. Exit
------------------------------"""


def ask(prompt: str, validator, **kwargs):
    """Keep prompting until the validator accepts the input."""
    while True:
        try:
            return validator(input(prompt), **kwargs)
        except ValueError as exc:
            print(f"  [!] {exc}")


def print_table(products: List[Product]) -> None:
    if not products:
        print("  No products to display.")
        return
    header = f"{'ID':<10}{'Name':<24}{'Category':<16}{'Qty':>6}{'Price':>11}{'Value':>12}"
    print(header)
    print("-" * len(header))
    for p in products:
        print(f"{p.product_id:<10}{p.name[:22]:<24}{p.category[:14]:<16}{p.quantity:>6}{p.price:>11.2f}{p.total_value:>12.2f}")


def add_product(inv: Inventory) -> None:
    while True:
        pid = ask("Product ID: ", v.validate_product_id)
        if inv.get(pid):
            print(f"  [!] ID '{pid}' already exists. Try another.")
            continue
        break
    name = ask("Name: ", v.validate_text, field="Name")
    category = ask("Category: ", v.validate_text, field="Category")
    qty = ask("Quantity: ", v.validate_quantity)
    price = ask("Price: ", v.validate_price)
    inv.add(Product(pid, name, category, qty, price))
    print(f"  [OK] Added '{name}'.")


def search_products(inv: Inventory) -> None:
    term = ask("Search (ID, name or category): ", v.validate_text, field="Search term")
    results = inv.search(term)
    print(f"\n  {len(results)} match(es):")
    print_table(results)


def update_product(inv: Inventory) -> None:
    pid = ask("Product ID to update: ", v.validate_product_id)
    p = inv.get(pid)
    if not p:
        print(f"  [!] No product with ID '{pid}'.")
        return
    print("  Press Enter to keep the current value.")
    changes = {}
    s = input(f"  Name [{p.name}]: ").strip()
    if s:
        changes["name"] = ask_value(s, v.validate_text, field="Name")
    s = input(f"  Category [{p.category}]: ").strip()
    if s:
        changes["category"] = ask_value(s, v.validate_text, field="Category")
    s = input(f"  Quantity [{p.quantity}]: ").strip()
    if s:
        changes["quantity"] = ask_value(s, v.validate_quantity)
    s = input(f"  Price [{p.price:.2f}]: ").strip()
    if s:
        changes["price"] = ask_value(s, v.validate_price)
    inv.update(pid, **changes)
    print("  [OK] Product updated." if changes else "  Nothing changed.")


def ask_value(first: str, validator, **kwargs):
    """Validate an already-entered value; re-prompt if invalid."""
    value = first
    while True:
        try:
            return validator(value, **kwargs)
        except ValueError as exc:
            print(f"  [!] {exc}")
            value = input("  Try again: ")


def delete_product(inv: Inventory) -> None:
    pid = ask("Product ID to delete: ", v.validate_product_id)
    p = inv.get(pid)
    if not p:
        print(f"  [!] No product with ID '{pid}'.")
        return
    if input(f"  Delete '{p.name}'? (y/n): ").strip().lower() == "y":
        inv.delete(pid)
        print("  [OK] Product deleted.")
    else:
        print("  Cancelled.")


def stock_move(inv: Inventory, incoming: bool) -> None:
    pid = ask("Product ID: ", v.validate_product_id)
    amount = ask("Quantity: ", v.validate_quantity, allow_zero=False)
    p = inv.stock_in(pid, amount) if incoming else inv.stock_out(pid, amount)
    print(f"  [OK] Stock {'added' if incoming else 'removed'}. '{p.name}' now has {p.quantity} unit(s).")


def low_stock_report(inv: Inventory) -> None:
    items = inv.low_stock(LOW_STOCK_THRESHOLD)
    print(f"\n  Low-stock items (quantity <= {LOW_STOCK_THRESHOLD}): {len(items)}")
    print_table(items)


def main() -> None:
    try:
        inv = Inventory(DATA_FILE)
    except StorageError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)

    actions = {
        "1": lambda: add_product(inv),
        "2": lambda: print_table(inv.products),
        "3": lambda: search_products(inv),
        "4": lambda: update_product(inv),
        "5": lambda: delete_product(inv),
        "6": lambda: stock_move(inv, True),
        "7": lambda: stock_move(inv, False),
        "8": lambda: print(f"\n  Total inventory value: {inv.total_value():,.2f}"),
        "9": lambda: low_stock_report(inv),
    }

    while True:
        print(MENU)
        try:
            choice = input("Choose an option: ").strip()
            if choice == "0":
                print("Goodbye!")
                break
            action = actions.get(choice)
            if action is None:
                print("  [!] Invalid option. Enter a number from 0 to 9.")
                continue
            print()
            action()
        except (InventoryError, StorageError) as exc:
            print(f"  [!] {exc}")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
