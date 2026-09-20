"""
CLI Contact Book
A simple command-line contact management application.

Features:
- Add, view, search, update, delete contacts
- Data persisted to a CSV file (contacts.csv)
- Input validation and error handling so the program never crashes
"""

import csv
import os
import re

DATA_FILE = "contacts.csv"
FIELDNAMES = ["name", "phone", "email"]


# ---------------------------------------------------------------------------
# File persistence
# ---------------------------------------------------------------------------

def load_contacts(filename=DATA_FILE):
    """Load contacts from the CSV file. Returns a list of dicts.
    If the file doesn't exist yet, returns an empty list (no crash)."""
    contacts = []
    if not os.path.exists(filename):
        return contacts

    try:
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Guard against malformed/blank rows
                if row.get("name"):
                    contacts.append(
                        {
                            "name": row.get("name", "").strip(),
                            "phone": row.get("phone", "").strip(),
                            "email": row.get("email", "").strip(),
                        }
                    )
    except (csv.Error, OSError) as e:
        print(f"Warning: could not read '{filename}' ({e}). Starting with an empty contact list.")
        return []

    return contacts


def save_contacts(contacts, filename=DATA_FILE):
    """Save the full contact list back to the CSV file."""
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(contacts)
    except OSError as e:
        print(f"Error: could not save contacts ({e}). Your changes may be lost.")


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def is_valid_phone(phone):
    """Allow digits, spaces, +, - . Require at least 7 digits total."""
    if not re.fullmatch(r"[0-9+\-\s]+", phone):
        return False
    digit_count = sum(ch.isdigit() for ch in phone)
    return digit_count >= 7


def is_valid_email(email):
    """Basic email format check: something@something.something"""
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None


def get_nonempty_input(prompt):
    """Keep asking until the user provides a non-blank value."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def get_valid_phone(prompt):
    while True:
        value = input(prompt).strip()
        if is_valid_phone(value):
            return value
        print("Invalid phone number. Use digits only (7+ digits), spaces, '+' or '-' allowed.")


def get_valid_email(prompt):
    while True:
        value = input(prompt).strip()
        if is_valid_email(value):
            return value
        print("Invalid email format. Example: name@example.com")


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def add_contact(contacts):
    print("\n--- Add New Contact ---")
    name = get_nonempty_input("Name: ")

    # Prevent exact duplicate names (case-insensitive), but allow user to override
    if any(c["name"].lower() == name.lower() for c in contacts):
        confirm = input(f"A contact named '{name}' already exists. Add anyway? (y/n): ").strip().lower()
        if confirm != "y":
            print("Add cancelled.")
            return

    phone = get_valid_phone("Phone number: ")
    email = get_valid_email("Email: ")

    contacts.append({"name": name, "phone": phone, "email": email})
    save_contacts(contacts)
    print(f"Contact '{name}' added successfully.")


def view_contacts(contacts):
    print("\n--- All Contacts ---")
    if not contacts:
        print("No contacts found.")
        return

    print(f"{'No.':<5}{'Name':<20}{'Phone':<18}{'Email':<30}")
    print("-" * 73)
    for i, c in enumerate(contacts, start=1):
        print(f"{i:<5}{c['name']:<20}{c['phone']:<18}{c['email']:<30}")


def search_contacts(contacts):
    print("\n--- Search Contacts ---")
    if not contacts:
        print("No contacts to search.")
        return

    query = input("Enter name or partial name to search: ").strip().lower()
    if not query:
        print("Search term cannot be empty.")
        return

    results = [c for c in contacts if query in c["name"].lower()]

    if not results:
        print(f"No contacts found matching '{query}'.")
        return

    print(f"\nFound {len(results)} match(es):")
    print(f"{'Name':<20}{'Phone':<18}{'Email':<30}")
    print("-" * 68)
    for c in results:
        print(f"{c['name']:<20}{c['phone']:<18}{c['email']:<30}")


def find_contact_index_by_name(contacts, name):
    """Return list of indices whose name matches (case-insensitive, exact)."""
    return [i for i, c in enumerate(contacts) if c["name"].lower() == name.lower()]


def update_contact(contacts):
    print("\n--- Update Contact ---")
    if not contacts:
        print("No contacts available to update.")
        return

    name = input("Enter the exact name of the contact to update: ").strip()
    matches = find_contact_index_by_name(contacts, name)

    if not matches:
        print(f"No contact found with the name '{name}'.")
        return

    # Handle duplicate names by letting the user pick which one
    if len(matches) > 1:
        print(f"Multiple contacts named '{name}' found:")
        for idx in matches:
            c = contacts[idx]
            print(f"  [{idx}] {c['name']} | {c['phone']} | {c['email']}")
        try:
            chosen = int(input("Enter the number in brackets [] to update: ").strip())
            if chosen not in matches:
                print("Invalid selection.")
                return
            target = chosen
        except ValueError:
            print("Invalid input. Update cancelled.")
            return
    else:
        target = matches[0]

    contact = contacts[target]
    print(f"Updating '{contact['name']}'. Press Enter to keep the current value.")

    new_name = input(f"New name [{contact['name']}]: ").strip()
    new_phone = input(f"New phone [{contact['phone']}]: ").strip()
    new_email = input(f"New email [{contact['email']}]: ").strip()

    if new_name:
        contact["name"] = new_name

    if new_phone:
        if is_valid_phone(new_phone):
            contact["phone"] = new_phone
        else:
            print("Invalid phone format entered — keeping the old phone number.")

    if new_email:
        if is_valid_email(new_email):
            contact["email"] = new_email
        else:
            print("Invalid email format entered — keeping the old email.")

    save_contacts(contacts)
    print("Contact updated successfully.")


def delete_contact(contacts):
    print("\n--- Delete Contact ---")
    if not contacts:
        print("No contacts available to delete.")
        return

    name = input("Enter the exact name of the contact to delete: ").strip()
    matches = find_contact_index_by_name(contacts, name)

    if not matches:
        print(f"No contact found with the name '{name}'.")
        return

    if len(matches) > 1:
        print(f"Multiple contacts named '{name}' found:")
        for idx in matches:
            c = contacts[idx]
            print(f"  [{idx}] {c['name']} | {c['phone']} | {c['email']}")
        try:
            chosen = int(input("Enter the number in brackets [] to delete: ").strip())
            if chosen not in matches:
                print("Invalid selection.")
                return
            target = chosen
        except ValueError:
            print("Invalid input. Delete cancelled.")
            return
    else:
        target = matches[0]

    confirm = input(f"Are you sure you want to delete '{contacts[target]['name']}'? (y/n): ").strip().lower()
    if confirm == "y":
        removed = contacts.pop(target)
        save_contacts(contacts)
        print(f"Contact '{removed['name']}' deleted.")
    else:
        print("Delete cancelled.")


# ---------------------------------------------------------------------------
# Menu / main loop
# ---------------------------------------------------------------------------

def print_menu():
    print("\n===== CLI CONTACT BOOK =====")
    print("1. Add Contact")
    print("2. View All Contacts")
    print("3. Search Contact")
    print("4. Update Contact")
    print("5. Delete Contact")
    print("6. Exit")


def main():
    contacts = load_contacts()
    print("Welcome to the CLI Contact Book!")
    print(f"Loaded {len(contacts)} contact(s) from '{DATA_FILE}'.")

    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            add_contact(contacts)
        elif choice == "2":
            view_contacts(contacts)
        elif choice == "3":
            search_contacts(contacts)
        elif choice == "4":
            update_contact(contacts)
        elif choice == "5":
            delete_contact(contacts)
        elif choice == "6":
            print("Goodbye! Your contacts have been saved.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Your saved contacts are safe in the CSV file. Goodbye!")
    except Exception as e:
        # Final safety net so the program never crashes with a raw traceback
        print(f"\nAn unexpected error occurred: {e}")
        print("The program will now exit safely.")
