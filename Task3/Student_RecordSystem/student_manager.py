#!/usr/bin/env python3
"""Student Record Management System (CLI) - Inovegen Internship, Task 3.

Features: add / view / search / update / delete students, persistent JSON storage,
input validation, graceful error handling, and a marks summary report.
"""
import json
import os
import re
import sys

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.json")
ID_RE = re.compile(r"^[A-Za-z0-9_-]{3,10}$")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'\-]{0,49}$")
COURSE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 .&+\-]{0,39}$")
GRADE_BANDS = [(90, "A"), (80, "B"), (70, "C"), (60, "D"), (50, "E"), (0, "F")]


class Cancelled(Exception):
    """Raised when the user types 'cancel' during a prompt."""


# ------------------------------------------------------------ validation
def parse_id(raw):
    raw = raw.strip()
    if not raw:
        raise ValueError("ID is required.")
    if not ID_RE.match(raw):
        raise ValueError("ID must be 3-10 characters: letters, digits, '-' or '_'.")
    return raw.upper()


def parse_name(raw):
    raw = " ".join(raw.split())
    if not raw:
        raise ValueError("Name is required.")
    if not NAME_RE.match(raw):
        raise ValueError("Name must start with a letter and use only letters, spaces, . ' - (max 50).")
    return raw.title()


def parse_course(raw):
    raw = " ".join(raw.split())
    if not raw:
        raise ValueError("Course is required.")
    if not COURSE_RE.match(raw):
        raise ValueError("Course may contain letters, digits, spaces and . & + - (max 40).")
    return raw


def parse_marks(raw):
    raw = raw.strip()
    if not raw:
        raise ValueError("Marks are required.")
    try:
        marks = float(raw)
    except ValueError:
        raise ValueError("Marks must be a number.") from None
    if marks != marks or marks in (float("inf"), float("-inf")):
        raise ValueError("Marks must be a finite number.")
    if not 0 <= marks <= 100:
        raise ValueError("Marks must be between 0 and 100.")
    return round(marks, 2)


def parse_menu_choice(raw, valid):
    raw = raw.strip()
    if raw not in valid:
        raise ValueError(f"Invalid choice '{raw}'. Enter one of: {', '.join(sorted(valid))}.")
    return raw


def grade_for(marks):
    for floor, letter in GRADE_BANDS:
        if marks >= floor:
            return letter


# ------------------------------------------------------------ persistence
def validate_record(rec):
    """Return a cleaned record or raise ValueError (used when loading from disk)."""
    if not isinstance(rec, dict):
        raise ValueError("record is not an object")
    try:
        return {
            "id": parse_id(str(rec["id"])),
            "name": parse_name(str(rec["name"])),
            "course": parse_course(str(rec["course"])),
            "marks": parse_marks(str(rec["marks"])),
        }
    except KeyError as e:
        raise ValueError(f"missing field {e}") from None


def load_students(path=None):
    """Load records; a missing file means an empty database, a corrupt one is backed up."""
    path = path or DATA_FILE
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("top level must be a list")
    except (OSError, ValueError) as e:        # json.JSONDecodeError is a ValueError
        backup = path + ".corrupt"
        try:
            os.replace(path, backup)
            print(f"Warning: could not read {os.path.basename(path)} ({e}). Backed up to {os.path.basename(backup)}; starting empty.")
        except OSError:
            print(f"Warning: could not read data file ({e}). Starting empty.")
        return []
    students, seen = [], set()
    for i, rec in enumerate(data, 1):
        try:
            clean = validate_record(rec)
            if clean["id"] in seen:
                raise ValueError("duplicate ID")
            seen.add(clean["id"])
            students.append(clean)
        except ValueError as e:
            print(f"Warning: skipped record #{i} in data file: {e}")
    return students


def save_students(students, path=None):
    """Atomic save (write temp file, then replace). Returns True on success."""
    path = path or DATA_FILE
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(students, f, indent=2)
        os.replace(tmp, path)
        return True
    except OSError as e:
        print(f"Error: could not save data ({e}). Your changes are NOT saved.")
        return False


# ------------------------------------------------------------ helpers
def find_by_id(students, sid):
    return next((s for s in students if s["id"] == sid), None)


def search_students(students, query):
    q = query.strip().lower()
    return [s for s in students
            if q == s["id"].lower() or q in s["name"].lower() or q in s["course"].lower()]


def compute_summary(students):
    if not students:
        return None
    marks = [s["marks"] for s in students]
    dist = {}
    for s in students:
        g = grade_for(s["marks"])
        dist[g] = dist.get(g, 0) + 1
    return {
        "count": len(students),
        "average": round(sum(marks) / len(marks), 2),
        "highest": [s for s in students if s["marks"] == max(marks)],
        "lowest": [s for s in students if s["marks"] == min(marks)],
        "grades": dist,
    }


def ask(prompt, parser, default=None):
    """Prompt until valid. Blank keeps `default` (if given). Typing 'cancel' aborts."""
    while True:
        shown = f"{prompt} [{default}]: " if default is not None else f"{prompt}: "
        raw = input(shown)
        if raw.strip().lower() == "cancel":
            raise Cancelled
        if default is not None and not raw.strip():
            return default
        try:
            return parser(raw)
        except ValueError as e:
            print(f"  Invalid input: {e}")


def print_table(rows):
    if not rows:
        print("No records to show.")
        return
    print(f"\n{'ID':<10} {'Name':<24} {'Course':<20} {'Marks':>6}  Grade")
    print("-" * 70)
    for s in sorted(rows, key=lambda r: r["id"]):
        print(f"{s['id']:<10} {s['name'][:24]:<24} {s['course'][:20]:<20} {s['marks']:>6.2f}  {grade_for(s['marks'])}")
    print(f"\n{len(rows)} record(s).")


# ------------------------------------------------------------ menu actions
def add_student(students):
    print("\n-- Add student (type 'cancel' to abort) --")
    while True:
        sid = ask("Student ID", parse_id)
        if find_by_id(students, sid):
            print(f"  ID {sid} already exists. Choose another.")
            continue
        break
    students.append({"id": sid, "name": ask("Name", parse_name),
                     "course": ask("Course", parse_course), "marks": ask("Marks (0-100)", parse_marks)})
    print("Saved." if save_students(students) else "Added in memory only.")


def view_students(students):
    print_table(students)


def search_menu(students):
    q = input("Search by ID, name or course: ").strip()
    if not q:
        print("Search text is required.")
        return
    print_table(search_students(students, q))


def update_student(students):
    print("\n-- Update student (blank keeps current value, 'cancel' aborts) --")
    s = find_by_id(students, ask("Student ID to update", parse_id))
    if not s:
        print("No student with that ID.")
        return
    new = {"name": ask("Name", parse_name, s["name"]),
           "course": ask("Course", parse_course, s["course"]),
           "marks": ask("Marks (0-100)", lambda r: parse_marks(r), s["marks"])}
    s.update(new)
    print("Updated and saved." if save_students(students) else "Updated in memory only.")


def delete_student(students):
    s = find_by_id(students, ask("Student ID to delete", parse_id))
    if not s:
        print("No student with that ID.")
        return
    if input(f"Delete {s['name']} ({s['id']})? Type 'yes' to confirm: ").strip().lower() == "yes":
        students.remove(s)
        print("Deleted and saved." if save_students(students) else "Deleted in memory only.")
    else:
        print("Deletion cancelled.")


def show_summary(students):
    r = compute_summary(students)
    if not r:
        print("No records yet - nothing to summarise.")
        return
    fmt = lambda rows: ", ".join(f"{s['name']} ({s['id']})" for s in rows)
    print("\n===== Summary =====")
    print(f"Students       : {r['count']}")
    print(f"Average marks  : {r['average']:.2f}")
    print(f"Highest marks  : {r['highest'][0]['marks']:.2f}  - {fmt(r['highest'])}")
    print(f"Lowest marks   : {r['lowest'][0]['marks']:.2f}  - {fmt(r['lowest'])}")
    print("Grades         : " + "  ".join(f"{g}:{n}" for g, n in sorted(r["grades"].items())))


MENU = {"1": ("Add student", add_student), "2": ("View all students", view_students),
        "3": ("Search students", search_menu), "4": ("Update student", update_student),
        "5": ("Delete student", delete_student), "6": ("Summary (avg / highest / lowest)", show_summary),
        "0": ("Exit", None)}


def main():
    students = load_students()
    print(f"Student Record Management System - {len(students)} record(s) loaded.")
    while True:
        print("\n===== MENU =====")
        for key, (label, _) in MENU.items():
            print(f" {key}. {label}")
        try:
            choice = parse_menu_choice(input("Choose an option: "), MENU)
            if choice == "0":
                print("Goodbye!")
                return 0
            MENU[choice][1](students)
        except Cancelled:
            print("Cancelled.")
        except ValueError as e:
            print(f"  {e}")
        except (KeyboardInterrupt, EOFError):
            print("\nInput ended. Goodbye!")
            return 0


if __name__ == "__main__":
    sys.exit(main())
