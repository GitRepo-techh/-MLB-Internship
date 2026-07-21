# -MLB-Internship
# MLB Internship
This repository tracks my daily progress during the MLB Internship, including concepts revised and hands-on Python/Git practice.

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

File: `Student Grading Sytem.py`

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

File: `student_record_system.py`

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
The main difficulty today was deciding how to set up `range()` correctly for each problem — specifically choosing the right start value, stop value, and step size (e.g. `range(2, 101, 2)` for even numbers, or `range(2, int(num ** 0.5) + 1)` for prime checks). It took some trial and error to get comfortable reasoning about where a range should start and end, and when a step other than 1 was needed.

**Dispatch Tables**
Once all the practice problems were written as separate functions, the program needed a way to let the user pick which one to run. Instead of a long `if-elif-else` chain to match a user's choice to a function call, I used a **dispatch table**: a dictionary that maps each menu option (as a string key) to the function it should call.

```python
tasks = {
    "1": integer,
    "2": even_odd,
}

tasks[choice]()   # looks up the function, then calls it
```

This kept the menu logic short and made it easy to add new problems by just adding a new entry to the dictionary, rather than adding another `elif` branch. The whole menu runs inside a single `while True` loop, so the program keeps prompting the user until they choose to exit.

File: `day3_conditionals_loops.py`

## 🛠️ Tech Stack
- Python 3
- Git & GitHub

## 🚀 How to Run
\`\`\`bash
python "Student Grading Sytem.py"
python "student_record_system.py"
python "day4_conditionals_loops.py"
\`\`\`

## 📌 Notes
More days and topics will be added here as the internship progresses.
