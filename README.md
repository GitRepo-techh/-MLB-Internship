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
The main challenge was a `KeyError` in the Student Record Management System — some records in `data.json` had leftover keys from earlier testing (`Class` instead of `Course`, or missing `Roll Number` entirely), which crashed `view_students()` since it expected every record to have the same schema. Fixed by changing the the json file created earleir and changing it's contents. Also ran into a Git merge conflict on `README.md` when pushing to GitHub, since the remote had changes that weren't present locally — resolved by pulling, manually choosing between the conflicting sections, and committing before pushing again.

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

# Day 5 - Object-Oriented Programming (OOP)

## Files in this folder
- `oop_practice.py` — Student, Employee, and Car classes, each with multiple objects created and demonstrated.
- `inheritance_practice.py` — Person (parent) class with Student and Teacher (child) classes, demonstrating method overriding and `super()`.
- `library_management_system.py` — Console-based Library Management System (mini project). Uses `Person → Student, Teacher` inheritance for library members, and `Book`/`Library` classes for the book catalogue. Data is saved to `library_data.json`, which is generated automatically the first time the program runs.

## What is Object-Oriented Programming?

OOP is a way of structuring code around **objects** — self-contained units that bundle together data (attributes) and behavior (methods) — instead of writing a long sequence of unrelated functions and variables.

Instead of managing a book as a loose collection of variables (`title`, `author`, `copies` floating around separately), OOP lets you define a `Book` class that holds all of that data together with the methods that operate on it (`borrow()`, `return_book()`). Each individual book is then an **object** — an instance of that class — with its own values for those attributes.

The four core ideas covered this week are:
- **Classes and Objects** — a class is the blueprint (e.g. `Book`); an object is a specific instance built from that blueprint (e.g. a copy of "Digital Design").
- **Inheritance** — a child class (e.g. `Student`) can reuse and extend the attributes/methods of a parent class (e.g. `Person`), avoiding duplicate code.
- **Encapsulation** — an object controls access to its own data, so it can only be changed through defined, rule-following methods rather than modified directly from anywhere in the program.
- **Polymorphism** — different classes can expose the same method names (e.g. `area()` on both `Circle` and `Rectangle`) and be used interchangeably.

## Where inheritance was used in this project

In `inheritance_practice.py`, `Student` and `Teacher` both inherit from a shared `Person` class. Both need a `name` and `age`, so that logic lives once in `Person.__init__`, and each child class calls `super().__init__(name, age)` to reuse it instead of repeating the same two lines. Each child class then overrides `role()` and extends `introduce()` with its own extra details (department/roll number for `Student`, subject/employee ID for `Teacher`).

In the Library Management System, the `Library` class doesn't inherit from `Book` — instead it *uses* `Book` objects (a "has-a" relationship rather than "is-a"), which is a deliberate design choice: a library isn't a type of book, so inheritance wouldn't make sense there. This distinction — knowing when *not* to use inheritance — was part of understanding when the concept actually applies.

## Challenges faced and how they were solved

- **Persisting objects to JSON:** JSON can't store Python objects directly, so each `Book` needed a `to_dict()` method to convert it into a plain dictionary before saving, and a `from_dict()` classmethod to rebuild a `Book` object when loading the file back in. This is the main bridge between "objects in memory" and "data on disk."
- **Handling a missing or corrupted JSON file:** On first run, `books.json` doesn't exist yet. This was handled with an `os.path.exists()` check, plus a `try/except` around `json.load()` to catch a corrupted or empty file (`json.JSONDecodeError`) so the program starts with an empty library instead of crashing.
- **Preventing invalid borrow/return actions:** A book shouldn't be borrowed if `available_copies` is already 0, or returned if all copies are already accounted for. This was enforced inside the `Book` class itself (`borrow()`/`return_book()` raise a `ValueError`), which is encapsulation in practice — the rule lives with the data it protects, not scattered around the menu-handling code.
- **Forgetting to write `self` in every method:** In the beginning I kept writing methods like `def borrow(radius):` instead of `def borrow(self, radius):` and Python would throw a `TypeError` about too many arguments. The reason `self` is needed is simple: when you call `book.borrow()`, Python is secretly turning that into `Book.borrow(book)` behind the scenes — it automatically passes the object itself as the first argument, so the method knows *which* object's data to work with. If `self` isn't there to catch it, Python has nowhere to put that object.
- **Calling `super()` without the parentheses:** I wrote `super.__init__(name, age)` instead of `super().__init__(name, age)` and got a confusing error (`descriptor '__init__' of 'super' object needs an argument`). `super` by itself is just the class, not a usable object — it has to be *called* with `()` first to actually get access to the parent class's methods. Easy to miss because it looks like it should work the same way as referring to `self`.

# Day 6: Python for Data Science — NumPy & Pandas

## What I Learned About NumPy

NumPy is the foundation library for numerical computing in Python — arrays support vector based operations, which makes them much faster than plain Python lists for numeric work. Every ML/data library (Pandas, scikit-learn, etc.) is built on top of it.

Key things I practiced:
- Creating 1D and 2D arrays with `np.array()`
- Indexing and slicing (`array[row, col]`, `array[:, col]`) — learned that slicing returns a **view**, not a copy, so editing a slice can change the original array
- The difference between indexing with a plain integer (collapses a dimension) vs. a slice range like `2:3` (keeps the dimension)
- Arithmetic operations (`+`, `*`) applied element-wise across arrays, no loops needed
- Aggregate functions: `.max()`, `.min()`, `.mean()`, `.sum()` — using NumPy's own methods instead of Python's built-in `max()`/`min()` for better performance on large arrays
- Reshaping arrays with `.reshape()` — learned the rule that while writing your paramters they should always multiply to whatever is the length of your array.
## What I Learned About Pandas

Pandas builds on NumPy to give you labeled, table form data structures — much closer to how real datasets look (rows and columns, like a spreadsheet).

Key things I practiced:
- **Series** (a single labeled column) vs. **DataFrame** (a full table)
- Loading data with `pd.read_csv()` and why file paths are relative to where you have opened teh file i.e the working directory, not the script's location.
- Exploring a dataset: `.head()`, `.tail()`, `.info()`, `.describe()`, `.shape`, `.columns`
- Finding missing values with `.isnull().sum()`
- Selecting columns with `df[["col1", "col2"]]` vs. filtering rows with boolean conditions like `df[df["col"] > value]`
- Combining multiple conditions with `&`/`|` (not `and`/`or` beacuse they are acustomed to compare a huge set of values at once while & operator is) — and why each condition needs its own parentheses due to operator precedence.
- Creating new columns by summing existing ones row-wise using `axis=1` in the min challenge.
- Sorting with `.sort_values()` and combining it with `.head()` to find top performers.
- Grouping with `.groupby()` for category-level aggregation (e.g., average score per program) — and understanding when to use `groupby` (comparing categories) vs .sorting/filtering (ranking or comparing individuals to a single value)
- Saving data back out with `.to_csv()`, and why `index=False` avoids writing pandas' internal row numbers into the file

## Key Insights From the Dataset

Using the student performance dataset (20 students, Python/Mathematics/Statistics/Machine_Learning scores + Attendance):

- No missing values in this dataset — a clean baseline for practicing.

- Average scores were fairly close across subjects (Python ~79, Mathematics ~79.5, Statistics ~80.6, Machine_Learning ~82.6), suggesting reasonably consistent performance across subjects rather than one subject dragging the average down.

- Grouping by `Program` showed differences in average performance and attendance between AI, DS, and SE tracks, which wouldn't have been visible from the raw table alone.

## Challenges I Faced

- **File paths**: got a `FileNotFoundError` because `pd.read_csv()` looks relative to the terminal's working directory, not the script's location — had to use the correct relative/full path.
- **Operator precedence in filters**: writing multi-condition filters without parentheses around each condition (e.g. `df["Program"] == "AI" & df["Attendance"] >= 90`) caused errors, since `&` binds tighter than `==`/`>=` in Python. Learned that you basically have to tell python that these need to be stored in round brackets as if following the `BODMAS` rule (e.g. `df[(df["Program"] == "AI") & (df["Attendance"] >= 90)]`) the extra df actaully helps python tell where exactly the `df[Program]` is located.
- **Row-wise vs. column-wise operations**: initially unclear on when to use `axis=1` vs the default `axis=0` when summing across subjects per student rather than summing a single column down.
- **Understanding views vs. copies**: NumPy slices return views by default confused the `:` operation with the slicing one as in `Numpy` it is used to view the cloumns or rows.
- **Boolean masks vs. filtered data**: mixed up printing a True/False condition (`ab["col"] <= value`) with actually filtering the dataframe (`ab[ab["col"] <= value]`) — needed to see both side by side to understand the difference. Basically understood why we needed two `ab[ab[]]`
## 📌 Notes
More days and topics will be added here as the internship progresses.