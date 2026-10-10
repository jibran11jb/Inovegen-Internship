# Inventory Management System

A command-line inventory manager built in Python for the Inovegen Internship (Task 4). It uses OOP, modular design, JSON persistence, and input validation.

## Features
- Add, view, search, update and delete products
- Each product stores: ID, name, category, quantity, price
- Data saved automatically to `data/inventory.json`
- Stock-in and stock-out (rejects zero, negative, or over-stock quantities)
- Total inventory value and low-stock report (default threshold: 10 units)
- Input validation and error handling; the app never crashes on bad input
- Clear numbered menu with meaningful messages

## Setup
Requires Python 3.8+. No external packages.

```bash
cd inventory_management_system
python main.py
```

Run the tests:
```bash
python -m unittest discover -s tests
```

## Usage
Pick an option from the menu (0-9) and follow the prompts.

| Option | Action |
|---|---|
| 1 | Add product |
| 2 | View all products |
| 3 | Search by ID, name or category |
| 4 | Update product (Enter keeps current value) |
| 5 | Delete product (asks for confirmation) |
| 6 / 7 | Stock in / Stock out |
| 8 | Total inventory value |
| 9 | Low-stock report |
| 0 | Exit |

## Project Structure
```
inventory_management_system/
├── main.py                 # CLI menu and user interaction
├── inventory/
│   ├── models.py           # Product dataclass
│   ├── manager.py          # Inventory class (business logic)
│   ├── storage.py          # JSON load/save
│   └── validators.py       # Input validation
├── data/inventory.json     # Sample data (6 products)
├── tests/test_inventory.py # Unit tests
├── screenshots/            # Feature screenshots
└── README.md
```

## Notes
- Product IDs are stored in uppercase and must be unique.
- To change the low-stock threshold, edit `LOW_STOCK_THRESHOLD` in `main.py`.
- A corrupted data file shows an error message instead of a crash.
