import csv
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"
DATE_FMT = "%Y-%m-%d"


class Expense:
    """A single expense record."""

    def __init__(self, expense_id, amount, category, date, description):
        self.id = expense_id
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d["id"], float(d["amount"]), d["category"], d["date"], d.get("description", ""))


class ExpenseTracker:
    """Manages a collection of expenses and their JSON persistence."""

    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.expenses = []
        self.load()

    # ---------- storage ----------
    def load(self):
        if not os.path.exists(self.filename):
            self.expenses = []
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.expenses = [Expense.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            print("Warning: data file is unreadable or corrupted. Starting with an empty list.")
            self.expenses = []

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([e.to_dict() for e in self.expenses], f, indent=4)
        except OSError as err:
            print(f"Error: could not save data ({err}).")

    # ---------- operations ----------
    def _next_id(self):
        return max((e.id for e in self.expenses), default=0) + 1

    def add(self, amount, category, date, description):
        expense = Expense(self._next_id(), amount, category, date, description)
        self.expenses.append(expense)
        self.save()
        return expense

    def find(self, expense_id):
        for e in self.expenses:
            if e.id == expense_id:
                return e
        return None

    def update(self, expense_id, amount=None, category=None, date=None, description=None):
        e = self.find(expense_id)
        if e is None:
            return False
        if amount is not None:
            e.amount = amount
        if category is not None:
            e.category = category
        if date is not None:
            e.date = date
        if description is not None:
            e.description = description
        self.save()
        return True

    def delete(self, expense_id):
        e = self.find(expense_id)
        if e is None:
            return False
        self.expenses.remove(e)
        self.save()
        return True

    def filter_by_category(self, category):
        return [e for e in self.expenses if e.category.lower() == category.lower()]

    def filter_by_date(self, start, end=None):
        end = end or start
        return [e for e in self.expenses if start <= e.date <= end]

    def total(self, items=None):
        items = self.expenses if items is None else items
        return sum(e.amount for e in items)

    def category_totals(self):
        totals = {}
        for e in self.expenses:
            key = e.category.title()
            totals[key] = totals.get(key, 0) + e.amount
        return totals

    def monthly_totals(self):
        totals = {}
        for e in self.expenses:
            month = e.date[:7]
            totals[month] = totals.get(month, 0) + e.amount
        return dict(sorted(totals.items()))

    def export_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Amount", "Category", "Date", "Description"])
            for e in self.expenses:
                writer.writerow([e.id, e.amount, e.category, e.date, e.description])


# ---------- input helpers ----------
def read_amount(prompt, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        try:
            value = float(raw)
            if value <= 0:
                print("  Amount must be greater than zero.")
                continue
            return round(value, 2)
        except ValueError:
            print("  Please enter a valid number.")


def read_date(prompt, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if raw == "":
            if allow_blank:
                return None
            return datetime.today().strftime(DATE_FMT)
        try:
            return datetime.strptime(raw, DATE_FMT).strftime(DATE_FMT)
        except ValueError:
            print("  Invalid date. Use YYYY-MM-DD (e.g. 2025-03-15).")


def read_text(prompt, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if raw or allow_blank:
            return raw or None
        print("  This field cannot be empty.")


def read_id(prompt):
    try:
        return int(input(prompt).strip())
    except ValueError:
        print("  Please enter a valid numeric ID.")
        return None


# ---------- display ----------
def print_table(items):
    if not items:
        print("\nNo expenses found.")
        return
    print(f"\n{'ID':<4} {'Date':<11} {'Category':<14} {'Amount':>10}  Description")
    print("-" * 65)
    for e in sorted(items, key=lambda x: x.date):
        print(f"{e.id:<4} {e.date:<11} {e.category:<14} {e.amount:>10.2f}  {e.description}")
    print("-" * 65)
    print(f"{'Total:':<31} {sum(e.amount for e in items):>10.2f}")


# ---------- menu actions ----------
def add_expense(tracker):
    print("\n--- Add Expense ---")
    amount = read_amount("Amount: ")
    category = read_text("Category: ")
    date = read_date("Date (YYYY-MM-DD, blank = today): ")
    description = read_text("Description: ", allow_blank=True) or ""
    e = tracker.add(amount, category, date, description)
    print(f"Expense #{e.id} added.")


def search_expenses(tracker):
    print("\n1. By category\n2. By date\n3. By date range")
    choice = input("Choose: ").strip()
    if choice == "1":
        print_table(tracker.filter_by_category(read_text("Category: ")))
    elif choice == "2":
        print_table(tracker.filter_by_date(read_date("Date (YYYY-MM-DD): ")))
    elif choice == "3":
        start = read_date("Start date: ")
        end = read_date("End date: ")
        if start > end:
            print("Start date must not be after end date.")
            return
        print_table(tracker.filter_by_date(start, end))
    else:
        print("Invalid choice.")


def show_totals(tracker):
    if not tracker.expenses:
        print("\nNo expenses recorded yet.")
        return
    print(f"\nOverall total: {tracker.total():.2f}")
    print("\nCategory-wise totals:")
    for cat, amt in sorted(tracker.category_totals().items()):
        print(f"  {cat:<15} {amt:>10.2f}")
    print("\nMonthly summary:")
    for month, amt in tracker.monthly_totals().items():
        print(f"  {month:<15} {amt:>10.2f}")


def update_expense(tracker):
    print("\n--- Update Expense ---")
    expense_id = read_id("Expense ID: ")
    if expense_id is None:
        return
    e = tracker.find(expense_id)
    if e is None:
        print("No expense with that ID.")
        return
    print("Press Enter to keep the current value.")
    amount = read_amount(f"Amount [{e.amount}]: ", allow_blank=True)
    category = read_text(f"Category [{e.category}]: ", allow_blank=True)
    date = read_date(f"Date [{e.date}]: ", allow_blank=True)
    description = read_text(f"Description [{e.description}]: ", allow_blank=True)
    tracker.update(expense_id, amount, category, date, description)
    print("Expense updated.")


def delete_expense(tracker):
    print("\n--- Delete Expense ---")
    expense_id = read_id("Expense ID: ")
    if expense_id is None:
        return
    if tracker.find(expense_id) is None:
        print("No expense with that ID.")
        return
    if input("Are you sure? (y/n): ").strip().lower() == "y":
        tracker.delete(expense_id)
        print("Expense deleted.")
    else:
        print("Cancelled.")


def export_expenses(tracker):
    path = input("CSV file name [expenses.csv]: ").strip() or "expenses.csv"
    if not path.lower().endswith(".csv"):
        path += ".csv"
    try:
        tracker.export_csv(path)
        print(f"Exported to {path}")
    except OSError as err:
        print(f"Could not export file ({err}).")


def main():
    tracker = ExpenseTracker()
    actions = {
        "1": add_expense,
        "2": lambda t: print_table(t.expenses),
        "3": search_expenses,
        "4": show_totals,
        "5": update_expense,
        "6": delete_expense,
        "7": export_expenses,
    }
    while True:
        print("\n===== EXPENSE TRACKER =====")
        print("1. Add expense")
        print("2. View all expenses")
        print("3. Search / filter")
        print("4. Totals and summaries")
        print("5. Update expense")
        print("6. Delete expense")
        print("7. Export to CSV")
        print("0. Exit")
        try:
            choice = input("Choose an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("Invalid option, please try again.")
            continue
        try:
            action(tracker)
        except KeyboardInterrupt:
            print("\nAction cancelled.")


if __name__ == "__main__":
    main()
