# MLB Internship

This repository tracks my daily progress during the MLB Internship, including concepts revised and hands-on Python/Git practice.

---

## 📅 Day 1

**Topics Revised**
- **Python Fundamentals:** Virtual Environments, Data Types, Variables, Data Structures (List, Tuple, Set, Dictionary), Functions, Conditional Operators
- **Git & GitHub Basics:** What is Git and GitHub, Creating a Repository, Cloning a Repository, Branching, Commit & Push Workflow

**Project: Student Grading System**
A Python program that:
- Accepts student name, class, and number of subjects
- Accepts marks per subject
- Calculates total and average marks
- Assigns grades (A/B/C/D/Fail) based on percentage thresholds
- Displays a formatted student report

**File:** `Student Grading System.py`

---

## 📅 Day 2

**Topics Revised**
- **Python Data Structures (Applied):** Lists of dictionaries for record management, nested data access
- **Functions & Control Flow:** Modular function design, input validation loops, `while True` menu-driven interfaces

**Project: Student Record Management System (Version 1)**
A menu-driven Python program that manages student records in memory using a list of dictionaries. Features include:
- Add Student — with input validation (non-empty fields, numeric age range check, duplicate roll number check)
- View All Students
- Search Student by Roll Number
- Update Student Information
- Delete Student
- Display Total Number of Students

**File:** `student_record_system.py`

---

## 📅 Day 3

**Overview**
Day 3 focused on control flow in Python — conditional statements and loops — and on applying them to a series of logic-building problems. The goal was to move beyond syntax and practice structuring a problem in plain English before writing any code.

**Concepts Covered**
- Conditional statements: `if`, `if-else`, `if-elif-else`, nested conditions
- Logical operators: `and`, `or`, `not`
- Loop constructs: `for` loop, `while` loop, `break`, `continue`, nested loops
- Problem-solving approach: understand the problem, describe the logic in plain English, break it into steps, then convert to code

**Practice Problems**

*Conditional Statements*
- Check whether a number is positive, negative, or zero
- Check whether a number is even or odd
- Grade calculator based on marks
- Find the largest among three numbers
- Check whether a year is a leap year

*Loops*
- Print numbers from 1 to 100
- Print all even numbers from 1 to 100
- Calculate the sum of numbers from 1 to N
- Print the multiplication table of a given number
- Count the number of digits in a number

*Logic Building*
- Reverse a number
- Check whether a number is a palindrome
- Generate the Fibonacci sequence
- Check whether a number is prime
- Find all prime numbers between 1 and 100

**Mini Challenge: Number Analysis Tool**
Combined several of the above checks into a single program. Given one number, it reports even/odd status, primality, digit count, the reversed number, and whether it is a palindrome, all in one formatted output.

**Challenges Faced**
The main difficulty was deciding how to set up `range()` correctly for each problem — specifically choosing the right start value, stop value, and step size (e.g. `range(2, 101, 2)` for even numbers, or `range(2, int(num ** 0.5) + 1)` for prime checks). It took some trial and error to get comfortable reasoning about where a range should start and end, and when a step other than 1 was needed.

**Dispatch Tables**
Once all the practice problems were written as separate functions, the program needed a way to let the user pick which one to run. Instead of a long `if-elif-else` chain to match a user's choice to a function call, a dispatch table was used — a dictionary that maps each menu option (as a string key) to the function it should call:

```python
tasks = {
    "1": integer,
    "2": even_odd,
}

tasks[choice]()   # looks up the function, then calls it
```

This kept the menu logic short and made it easy to add new problems by just adding a new entry to the dictionary, rather than adding another `elif` branch. The whole menu runs inside a single `while True` loop, so the program keeps prompting the user until they choose to exit.

**File:** `day3_conditionals_loops.py`

---

## 📅 Day 4 — File Handling & JSON

### 1. File Handling Basics
- Opening files in different modes: `"w"` (write), `"a"` (append), `"r"` (read)
- Why `open()` doesn't create missing directories — only the file itself
- Using `os.getcwd()` and `os.listdir()` to debug relative path issues
- Raw strings (`r"..."`) for Windows file paths, to avoid backslash escape-character bugs
- `with open(...) as f:` vs manual `open()`/`close()` — `with` auto-closes the file even if an error occurs
- `file.write()` returns the number of characters written, not the text itself

### 2. Reading Files
- `.read()` → returns the entire file as one string
- `.readlines()` → returns a list of lines, split on `\n`
- Looping directly over a file object (`for line in file:`) as a memory-efficient alternative to `.readlines()`
- Key insight: `.readlines()` only splits where `\n` actually exists in the file — no newline written, no separate lines read back
- Counting lines with `len(line)` on the *list*, not on each individual line (which instead gives character count)

### 3. JSON
JSON structure mirrors Python lists/dicts closely, with key differences:
- Double quotes required (not single)
- `true` / `false` / `null` instead of `True` / `False` / `None`
- No trailing commas

Standard shape for multiple records: **a list of dictionaries**, e.g.
```json
[
    {"Name": "M.fa", "Roll Number": "2025-CE-101"},
    {"Name": "M.ee", "Roll Number": "2025-CE-102"}
]
```

- `json.dump(data, f, indent=4)` — writes Python data to a file as formatted JSON
- `json.load(f)` — reads JSON from a file back into Python objects
- **You cannot "append" to a JSON list by opening in `"a"` mode** — it just tacks on raw text and breaks the JSON structure. Correct pattern:
  1. Read the existing JSON into memory (`"r"` mode)
  2. Modify the Python list/dict
  3. Write the entire updated structure back (`"w"` mode)

### 4. Mini Project — Student Record Management System (Persistent Version)
Upgraded the console-based CRUD system to persist data to `data.json`:
- `load_data()` — reads existing records on startup; falls back to prebuilt sample students if no file exists yet
- `save_data()` — writes the current `students` list back to disk after every add/update/delete
- Avoided using `global` inside `load_data()` by mutating the list in place with `.clear()` + `.extend()` instead of reassigning it
- Debugged a `KeyError: 'Roll Number'` caused by stale test data (different schema) sitting in `data.json` from earlier experiments — fixed by aligning all records to the same keys: `Name`, `Roll Number`, `Age`, `Course`

**File:** `Mini Challenge` / `Json_practice.py` / `file_handling.py`

### Reflection

**What I learned today**
How Python handles files at a low level — opening in different modes (`r`, `w`, `a`), reading content back with `.read()` vs `.readlines()`, and why `with` is the safer way to manage file handles since it auto-closes them. Also learned JSON from the ground up: how it maps to Python lists/dicts, its stricter syntax rules, and how to read and write it using the `json` module.

**How file handling and JSON work together**
JSON is just structured text at the end of the day, so it still relies on normal file handling to get on and off disk. `json.dump()` and `json.load()` don't work with file paths directly — they need an open file object, which is why they're always used inside a `with open(...) as f:` block. The important nuance is that JSON can't be appended to like plain text: since the whole file is one JSON structure (like a list of dicts), adding a new record means reading the whole file in, modifying the Python object in memory, then rewriting the entire file back out.

**Challenges I faced**
The main challenge was a `KeyError` in the Student Record Management System — some records in `data.json` had leftover keys from earlier testing (`Class` instead of `Course`, or missing `Roll Number` entirely), which crashed `view_students()` since it expected every record to have the same schema. Fixed by manually aligning all records to the same set of keys. Also ran into a Git merge conflict on `README.md` when pushing to GitHub, since the remote had changes that weren't present locally — resolved by pulling, manually choosing between the conflicting sections, and committing before pushing again.

**Next Steps / To-Do**
- Add `.get()` fallbacks in `view_students()` so a missing key shows `"N/A"` instead of crashing
- Consider re-adding exception handling (`try`/`except`) around file I/O for corrupted or missing JSON files

---

## 🛠️ Tech Stack
- Python 3
- Git & GitHub

## 🚀 How to Run
```bash
python "Student Grading System.py"
python "student_record_system.py"
python "day3_conditionals_loops.py"
python "Day4/Mini Challenge"
```

## 📌 Notes
More days and topics will be added here as the internship progresses.