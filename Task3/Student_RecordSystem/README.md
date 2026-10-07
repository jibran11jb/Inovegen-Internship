# Student Record Management System (CLI)
**Inovegen Internship – Task 3: Python Programming**

A menu-driven command-line program to manage student records with persistent JSON storage.
Pure Python 3 – **no external libraries**.

## Setup
1. Install Python 3.8 or newer (`python --version` to check).
2. Put `student_manager.py` and `students.json` in the same folder.

## Run
```bash
python student_manager.py        # use python3 on macOS/Linux
```
Run the automated tests (optional):
```bash
python tests/test_student_manager.py
```

## Features
| Menu | Function |
|---|---|
| 1 | **Add** a student (ID, name, course, marks) |
| 2 | **View** all students in a formatted table with letter grades |
| 3 | **Search** by ID, part of a name, or course (case-insensitive) |
| 4 | **Update** a student – press Enter to keep a current value |
| 5 | **Delete** a student (asks for `yes` confirmation) |
| 6 | **Summary** – student count, average marks, highest and lowest marks (with names), grade distribution |
| 0 | Exit |

Type `cancel` at any prompt while adding/updating/deleting to abort that action.

## Data file (`students.json`)
Records are saved automatically after every add/update/delete. A sample file with 8 students is included.
```json
{"id": "S001", "name": "Ayesha Khan", "course": "Computer Science", "marks": 92.5}
```
- Writes are atomic (temp file + replace) so a crash cannot leave a half-written file.
- Missing file → starts with an empty database and creates it on first save.
- Corrupt file → backed up as `students.json.corrupt`, program starts empty (no crash).
- Invalid or duplicate records inside the file are skipped with a warning.

## Validation & error handling
| Field | Rule |
|---|---|
| ID | 3–10 characters: letters, digits, `-`, `_`; stored upper-case; must be unique |
| Name | Required; starts with a letter; letters, spaces, `. ' -`; max 50 |
| Course | Required; letters, digits, spaces, `. & + -`; max 40 |
| Marks | Number from 0 to 100 (decimals allowed; `nan`/`inf` rejected) |
| Menu choice | Must be one of the listed options |

Invalid input shows a message and asks again – the program never crashes. `Ctrl+C` / `Ctrl+D` exit cleanly,
and file I/O errors are reported without losing the in-memory session.

**Grade scale:** A ≥ 90 · B ≥ 80 · C ≥ 70 · D ≥ 60 · E ≥ 50 · F < 50

## Code structure (`student_manager.py`)
- `parse_*` functions – validation (raise `ValueError` with a friendly message)
- `load_students` / `save_students` – JSON persistence
- `find_by_id`, `search_students`, `compute_summary`, `grade_for` – logic (testable, no I/O)
- `add_student`, `view_students`, `search_menu`, `update_student`, `delete_student`, `show_summary` – menu actions
- `ask()` – reusable prompt-until-valid helper; `main()` – menu loop

## Example session
```
Choose an option: 6
===== Summary =====
Students       : 8
Average marks  : 73.38
Highest marks  : 97.00  - Zainab Iqbal (S007)
Lowest marks   : 43.75  - Omar Farooq (S008)
Grades         : A:2  B:1  C:2  D:1  E:1  F:1
```
