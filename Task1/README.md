# CLI Contact Book

A simple command-line contact management application built with core Python (no external libraries).

## Features

- **Add Contact** — Enter name, phone, and email (validated before saving).
- **View All Contacts** — Displays all contacts in a formatted table.
- **Search Contact** — Search by full or partial name (case-insensitive).
- **Update Contact** — Edit an existing contact's name, phone, or email. Press Enter to keep the current value.
- **Delete Contact** — Remove a contact after confirmation.
- **Persistent Storage** — All contacts are saved to `contacts.csv` and reloaded automatically the next time the program runs.
- **Input Validation & Error Handling** — Invalid phone numbers, invalid emails, empty fields, bad menu choices, and unexpected errors are all handled gracefully without crashing the program.

## Requirements

- Python 3.6+
- No external packages needed (uses only the standard library: `csv`, `os`, `re`)

## Setup & How to Run

1. Make sure `contact_book.py` and `contacts.csv` are in the same folder.
2. Open a terminal in that folder.
3. Run:
   ```
   python3 contact_book.py
   ```
   (On Windows, use `python contact_book.py`)
4. Follow the on-screen menu (options 1–6).

If `contacts.csv` does not exist yet, the program will start with an empty contact list and create the file automatically the first time you add a contact.

## File Structure

```
contact_book/
├── contact_book.py   # Main program (all logic, organized into functions)
├── contacts.csv       # Sample data file (5 pre-loaded contacts)
└── README.md          # This file
```

## Validation Rules

- **Name**: cannot be empty.
- **Phone**: digits, spaces, `+`, and `-` only; must contain at least 7 digits.
- **Email**: must match the basic pattern `something@something.something`.
- Menu choices outside 1–6, non-numeric input, and file read/write errors are all caught and reported without stopping the program.

## Notes

- Duplicate names are allowed but flagged with a confirmation prompt when adding; update/delete let you pick the exact record if duplicates exist.
- The program exits cleanly on `Ctrl+C` without losing already-saved data.
