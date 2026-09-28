# Task 2 – Expense Tracker (Python)

A command-line expense tracker that stores data in a JSON file and uses a simple object-oriented design.

## Features
- Add an expense (amount, category, date, description)
- View all expenses in a table
- Search / filter by category, single date, or date range
- Overall total and category-wise totals
- Monthly summary (bonus)
- Update and delete expenses
- Export to CSV (bonus)
- Data saved automatically to `expenses.json`
- Input validation (positive numbers, `YYYY-MM-DD` dates, non-empty fields) and error handling for missing or corrupted files, so the program does not crash

## Project Structure
```
Task2/
├── expense_tracker.py   # source code
├── expenses.json        # sample data
├── README.md
└── screenshots/
```

## Code Overview
- `Expense` class – one expense record (converts to/from dictionary for JSON)
- `ExpenseTracker` class – add, update, delete, filter, totals, JSON load/save, CSV export
- Helper functions for validated input, plus menu functions and `main()`

## Setup and Run
1. Install Python 3.8 or newer (no extra libraries needed).
2. Open Command Prompt or PowerShell in the project folder.
3. Run:
   ```
   python expense_tracker.py
   ```
4. Follow the on-screen menu. Enter `0` to exit.

## Notes
- Dates use the format `YYYY-MM-DD` (press Enter to use today's date when adding).
- If `expenses.json` does not exist, it is created on the first save.
