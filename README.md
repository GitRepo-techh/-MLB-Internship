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


# Day 7 – Data Cleaning & Visualization

Student performance analysis using Pandas, Matplotlib, and Seaborn.

## Data Cleaning Steps

1. **Loaded** `student_performance.csv` with `pandas.read_csv()`.
2. **Checked for missing values** using `df.isnull().sum()` — dataset had 0 missing values across all 9 columns.
3. **Checked for duplicate rows** using `df.duplicated().sum()` — 0 duplicates found.
4. **Applied `dropna()` and `drop_duplicates()` anyway**, as defensive practice, even though they were no-ops on this dataset (real-world data pipelines shouldn't assume clean input).
5. **Verified data types** with `df.dtypes` — subject scores were already correctly typed as `int64`; no type conversion was needed.
6. **Created `Average_Score`** — row-wise mean of the four subject columns (`Python`, `Mathematics`, `Statistics`, `Machine_Learning`) using `.mean(axis=1)`.
7. **Created `Performance`** — categorized each student using `pd.cut()` with bins `[0, 70, 80, 90, 101]` and labels `Needs Improvement / Average / Good / Excellent`, using `right=False` so boundary scores (e.g. exactly 80 or 90) fall into the correct higher category.
8. **Saved the cleaned dataset** as `cleaned_student_performance.csv`.

## Visualizations Created

| Chart | Purpose |
|---|---|
| Bar Chart | Average score per student |
| Histogram | Distribution of Average Scores across the class |
| Scatter Plot | Python marks vs Machine Learning marks (checking correlation) |
| Pie Chart | Breakdown of students by Performance category |
| Box Plot | Spread and outliers of marks across all four subjects |
| Bar Chart (dashboard) | Average score per subject |
| Bar Chart (dashboard) | Top 5 performing students |


## Here is the link for the app:
http://localhost:8501

## Key Insights

1. **Machine Learning is the class's strongest subject, Python the weakest.** Subject averages: Python 78.9, Mathematics 79.5, Statistics 80.6, Machine Learning 82.6 — a nearly 4-point gap between the highest and lowest averaging subjects.

2. **Python and Machine Learning scores are very strongly correlated** (r ≈ 0.98) — students who score well in Python almost always score well in Machine Learning, suggesting the two skills reinforce each other rather than being independent.

3. **The class splits evenly between strong and struggling performers.** 10 of 20 students (50%) fall into "Good" or "Excellent," while 4 students (20%) fall into "Needs Improvement" — most notably Hassan Tariq (58.75) and Danish Ali (64.00), who are furthest from the class average and may benefit from targeted support.



# Day 8 — Data Preprocessing & First ML Model (Student Score Prediction System)

## What I Learned About Data Preprocessing

- **Not every column is a feature.** Identifier columns like `Student_ID` and `Name` carry no real predictive relationship with the target — they had to be dropped, otherwise the model would either ignore them or overfit to meaningless noise.
- **Avoiding a circular target.** My target, `Average_score`, is the mean of `Python`, `Mathematics`, `Statistics`, and `Machine_Learning`. Using those same four columns as features would let the model just do arithmetic instead of actually learning a relationship — so the real features I used were `Age`, `Attendance`, and `Program` instead.
- **Categorical encoding.** `Program` (`AI`, `SE`, `DS`) is a **nominal** category — no natural order — so I used **One-Hot Encoding** (`OneHotEncoder(drop="first")`) rather than Label Encoding, which is meant for **ordinal** categories where order matters (e.g. Low/Medium/High).
- **Feature scaling.** I standardized `Age` and `Attendance` using `StandardScaler` so both features are on a comparable scale (mean 0, standard deviation 1) before training.
- **Data leakage.** The scaler and encoder must be **fit only on training data**, then just **applied (transformed)** to the test data. Fitting on the full dataset before splitting would let information from the test set leak into training, making evaluation metrics look better than they really are.

## Why Train-Test Splitting Is Important

Splitting data into training and testing sets lets you check whether a model has actually learned a generalizable pattern, or just memorized the training data. Training and evaluating on the same data would give a falsely optimistic performance score with no way to know how the model handles new, unseen students. I used an 80/20 split (`train_test_split(..., test_size=0.2, random_state=42)`), with `random_state` fixed so the split — and therefore my results — are reproducible on every run.

## Evaluation Metrics Used

- **MAE (Mean Absolute Error)** — average size of prediction errors, in the same units as the score.
- **MSE (Mean Squared Error)** — similar to MAE, but squares errors first, so larger mistakes are penalized more heavily.
- **R² Score** — proportion of variance in the actual scores that the model explains (1.0 = perfect fit, 0 = no better than predicting the mean, negative = worse than predicting the mean).

## Model Performance & Observations

> Fill in your actual printed values here after running `app.py` or the script — they'll vary slightly depending on the random train-test split:

- MAE: `___`
- MSE: `___`
- R² Score: `___`

**Observations:**
- With only 20 rows total, the test set is just 4 rows (at an 80/20 split). This is a very small sample to judge model performance on — R² in particular can look unstable or even negative purely due to dataset size, not necessarily a flaw in the model or code.
- Points on the Actual vs Predicted scatter plot that fall close to the red diagonal line are accurate predictions; points that scatter far from it show where the model struggled.
- A larger, more varied dataset (more students, more spread in attendance/age/program) would likely give a more stable and trustworthy evaluation.

## Files

- `app.py` — Streamlit app implementing the full pipeline: load → preprocess (target creation, encoding, scaling) → train-test split → train Linear Regression → evaluate (MAE/MSE/R²) → Actual vs Predicted table → scatter plot → live prediction on new input.
- `student_performance.csv` — dataset (optional to include; `app.py` falls back to a built-in sample dataset if this file isn't present, and also supports uploading a CSV directly in the app).

## Run It

```powershell
uv run streamlit run app.py
```


# Day 9 — Model Evaluation & Classification

## What is Classification?

Classification is a supervised machine learning task where the model predicts a
**discrete category (class label)** rather than a continuous number. The model
learns from labeled examples and assigns new, unseen data points to one of a
fixed set of classes.

Example in this project: given four flower measurements (sepal length, sepal
width, petal length, petal width), predict which of three Iris species
(*setosa*, *versicolor*, *virginica*) the flower belongs to.

## Regression vs Classification

| | Regression | Classification |
|---|---|---|
| Output | Continuous numeric value | Discrete class/category |
| Example | Predicting house price | Predicting flower species |
| Algorithms | Linear Regression | Logistic Regression, Decision Trees |
| Evaluation | MAE, MSE, R² | Accuracy, Precision, Recall, F1, Confusion Matrix |

Regression answers "how much / how many?" while classification answers
"which category?"

## Real-World Classification Examples

- Email spam detection (spam / not spam)
- Medical diagnosis (disease present / absent)
- Loan default prediction (default / no default)
- Sentiment analysis (positive / negative / neutral)

## Evaluation Metrics Used

- **Accuracy** — percentage of total predictions that were correct. Can be
  misleading on imbalanced datasets.
- **Precision** — of everything the model predicted as a given class, how
  many were actually that class. Matters when false positives are costly.
- **Recall** — of everything that actually belongs to a class, how many did
  the model correctly find. Matters when false negatives are costly.
- **F1-Score** — harmonic mean of precision and recall; a single balanced
  metric when both false positives and false negatives matter.
- **Confusion Matrix** — a table showing actual vs. predicted labels per
  class, revealing exactly *where* the model gets confused (e.g. mixing up
  versicolor and virginica), not just an overall score.

Since Iris is a **multi-class, balanced** dataset, macro-averaged precision,
recall, and F1 were used (each class weighted equally).

## Model Performance & Observations

| Metric | Logistic Regression | Decision Tree (max_depth=3) |
|---|---|---|
| Accuracy | 0.9667 | 0.9667 |
| Precision (macro) | 0.9697 | 0.9697 |
| Recall (macro) | 0.9667 | 0.9667 |
| F1-Score (macro) | 0.9666 | 0.9666 |

**Confusion Matrix (both models, test set of 30):**
```
[[10  0  0]   setosa      -> all 10 correctly classified
 [ 0  9  1]   versicolor  -> 1 misclassified as virginica
 [ 0  0 10]]  virginica   -> all 10 correctly classified
```

**Observations:**
- *Setosa* is perfectly separated in every run — its petal measurements are
  distinctly different from the other two species, so both models classify
  it with 100% accuracy.
- The only confusion happens between *versicolor* and *virginica*, which
  have overlapping petal length/width ranges — this is a well-known
  characteristic of the Iris dataset, not a modeling flaw.
- Logistic Regression and the depth-limited Decision Tree performed
  identically on this split, which makes sense: Iris classes are nearly
  linearly separable, so a linear decision boundary (Logistic Regression)
  is already close to optimal, and a shallow tree just approximates similar
  boundaries with axis-aligned splits.
- An unconstrained (unpruned) Decision Tree can overfit the training data
  perfectly but perform worse on unseen data — this is why `max_depth=3` was
  used, tying back to today's overfitting/underfitting topic.

## Live App

🔗 **Streamlit App:** [add your deployed link here after deploying, e.g. https://mlb-internship-day9-yourname.streamlit.app]

The app has three tabs:
- **📊 Dataset** — dataset preview, class balance, statistical summary, feature pairplot
- **🎯 Model Evaluation** — accuracy/precision/recall/F1 and confusion matrix for both Logistic Regression and Decision Tree
- **🔮 Try a Prediction** — interactive sliders for the four flower measurements, returns predicted species with class probabilities

## Files in this folder

- `classification_practice.py` — Day 9 coding practice tasks (load, explore,
  split, train Logistic Regression, evaluate, confusion matrix)
- `iris_classification_project.py` — Mini project: full Iris Flower
  Classification System with Logistic Regression + bonus Decision Tree
  comparison
- `app.py` — Streamlit web app version of the classification system
  (Dataset / Model Evaluation / Try a Prediction tabs)
- `requirements.txt` — dependencies needed to run/deploy `app.py`
- `confusion_matrix.png` / `confusion_matrix_logistic_regression.png` /
  `confusion_matrix_decision_tree.png` — confusion matrix screenshots
- `iris_pairplot.png` — exploratory data visualization
- `model_comparison.csv` — side-by-side metric comparison

## How to Run

**Run the practice/project scripts:**
```bash
pip install scikit-learn pandas matplotlib seaborn
python classification_practice.py
python iris_classification_project.py
```

**Run the Streamlit app locally:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Deploy the app for a public link (used for the Discord/submission link):**
1. Push this folder to the `MLB-Internship` GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click "New app" → select this repo → set main file path to `Day-9/app.py`
4. Click Deploy — you'll get a public `https://...streamlit.app` link


# Day 10 — Model Evaluation & Hyperparameter Tuning (Breast Cancer Prediction System)

## What is Model Evaluation?

Training a model is only half the job — evaluation is how you find out whether
it actually generalizes, or just memorized the training set. Today's focus was
on the workflow that comes *after* `model.fit()`: measuring performance
properly, understanding *why* a model over/underperforms, and then improving
it in a structured way rather than guessing at parameters.

**Topics Covered**
- Train vs. Test performance — comparing scores on both sets to spot a gap
  that signals over/underfitting
- Underfitting vs. Overfitting — a model too simple to capture the pattern
  vs. one that has memorized noise in the training data
- Cross-Validation — splitting the training data into multiple folds so a
  model's score isn't dependent on one lucky/unlucky split
- Learning Curves (concept) — plotting training size vs. score to visualize
  whether more data would help, or whether the model has plateaued
- Choosing the right evaluation metric — accuracy isn't always the right
  call, especially on imbalanced or high-stakes classification tasks (e.g.
  medical diagnosis, where **recall** matters more than accuracy)

## What is Hyperparameter Tuning?

Hyperparameters are settings chosen *before* training (e.g. `C`, `penalty`,
`solver` for Logistic Regression) — as opposed to parameters the model learns
on its own (the coefficients). Picking good hyperparameters can meaningfully
change a model's performance, but testing every combination by hand doesn't
scale.

- **GridSearchCV** — exhaustively tries every combination in a parameter grid,
  cross-validating each one, and returns the best-scoring combination
- **RandomizedSearchCV (concept)** — samples a fixed number of random
  combinations instead of every single one, trading a small amount of
  thoroughness for much faster search on large grids
- Why tuning matters — the default hyperparameters are a reasonable starting
  point, not necessarily the best fit for a specific dataset
- Selecting the best model — `GridSearchCV` exposes `.best_params_`,
  `.best_score_`, and `.best_estimator_` so the tuned model can be evaluated
  the same way as the baseline for a fair comparison

## Practice: Breast Cancer Wisconsin Dataset

Using the built-in Scikit-learn dataset:
1. Loaded the data and converted it into a Pandas DataFrame; explored it with
   `.head()`, `.info()`, `.describe()`, and checked the target class balance
2. **Baseline model** — split the data (80/20, stratified), scaled features
   with `StandardScaler`, trained a plain `LogisticRegression`, and evaluated
   it with Accuracy, Precision, Recall, F1-Score, and a confusion matrix
3. **Hyperparameter tuning** — ran `GridSearchCV` (`cv=5`, scoring=`recall`)
   over a grid of `C`, `penalty`, and `solver` values, then compared the tuned
   model's metrics against the baseline

## Evaluation Metrics Used

- **Accuracy** — overall percentage of correct predictions
- **Precision** — of predicted-malignant cases, how many were truly malignant
- **Recall** — of truly malignant cases, how many the model actually caught
  (chosen as the `GridSearchCV` scoring metric, since missing a malignant
  case is far more costly than a false alarm)
- **F1-Score** — balances precision and recall into one number
- **Confusion Matrix** — visualizes exactly which cases were mixed up, and in
  which direction

## Model Performance & Observations

> Fill in your actual printed values here after running the pipeline:

| Metric | Baseline | Tuned |
|---|---|---|
| Accuracy | `___` | `___` |
| Precision | `___` | `___` |
| Recall | `___` | `___` |
| F1-Score | `___` | `___` |

**Best Parameters (GridSearchCV):** `___`

**Observations:**
- Tuning didn't necessarily beat the baseline on every metric — with `recall`
  as the scoring target, `GridSearchCV` explicitly favors catching more true
  positives, sometimes at a small cost to precision or accuracy.
- The baseline model already performs strongly on this dataset (it's a fairly
  clean, well-separated one), so gains from tuning are often modest — the
  value of the exercise is in the *process* of comparing before/after fairly,
  not necessarily a dramatic score jump.

## Mini Project — Breast Cancer Prediction System (Streamlit App)

Built a full Streamlit app around the pipeline instead of a script with
printed output, so the workflow is interactive and shareable:

- **📊 Data Exploration** — key metric cards (samples, features, class
  counts, missing-value check), a target-class pie chart, an interactive
  per-feature histogram (pick any feature, see its distribution split by
  class), and a boxplot comparing the highest-variance features across
  classes — replacing raw `.info()`/`.describe()` text dumps with visuals
- **📈 Baseline Model** — trains the untuned `LogisticRegression`, shows its
  metrics and confusion matrix
- **🔧 Hyperparameter Tuning** — runs `GridSearchCV`, displays the best
  parameters/CV score, and the tuned model's metrics and confusion matrix
- **⚖️ Comparison** — a side-by-side baseline vs. tuned metrics table with a
  per-metric improvement column, plus a grouped bar chart

Sidebar controls (test size, random state, CV folds, scoring metric) let you
re-run the whole pipeline with different settings without touching the code.

## Challenges Faced

- Deciding what belonged on the front page vs. behind a button — the first
  version of the app dumped raw `df.info()`/`df.describe()` output straight
  onto the page, which read as cluttered and code-like rather than a
  presentable dashboard. Replaced both with metric cards and charts, and
  tucked the raw row preview into a collapsed expander instead.
- `st.cache_data` vs. `st.cache_resource` — DataFrames and split arrays use
  `cache_data`, but the trained model objects (`LogisticRegression`,
  `GridSearchCV`) needed `cache_resource` instead, since they aren't
  plain serializable data.

## Files

- `breast_cancer_classification.py` — practice script covering baseline
  training, `GridSearchCV` tuning, and before/after comparison
- `app.py` — Streamlit app implementing the full pipeline: load → explore →
  scale → baseline model → `GridSearchCV` tuning → evaluate → confusion
  matrices → comparison

## Run It

```powershell
uv add streamlit scikit-learn seaborn matplotlib pandas
uv run streamlit run app.py
```

# Day 11 — Unsupervised Learning: Clustering & Dimensionality Reduction

## Overview

This folder contains my work on unsupervised learning techniques, applied to the Iris dataset (built into scikit-learn). The two techniques covered are **K-Means Clustering** and **Principal Component Analysis (PCA)**.

Unlike supervised learning, unsupervised learning works without target labels — the goal is to discover hidden structure or patterns in the data on its own.

## What is Clustering?

Clustering is the task of grouping similar data points together based on how close they are to each other, without being told in advance what the groups should be. **K-Means** is one common clustering algorithm:

1. Choose a number of clusters, K
2. Randomly place K centroids
3. Assign every data point to its nearest centroid
4. Move each centroid to the average position of the points assigned to it
5. Repeat steps 3–4 until the centroids stop moving (convergence)

## What is PCA?

PCA (Principal Component Analysis) is a dimensionality reduction technique. It compresses data with many features down into fewer new features (principal components), while preserving as much of the original variance (information) as possible.

- **PC1** is the direction of maximum variance in the data
- **PC2** is the direction of the next-highest variance, constrained to be perpendicular (orthogonal) to PC1

Data points are then re-plotted using their projection onto PC1 and PC2 instead of their original features — making high-dimensional data visualizable in 2D.

PCA matters here because the Iris dataset has 4 features (sepal length, sepal width, petal length, petal width), which can't be visualized directly on one 2D plot. PCA compresses those 4 features down to 2, while keeping most of the meaningful structure intact.

## How I Determined the Best Value of K

I used the **Elbow Method**: fit K-Means for K = 1 through 7, recorded the `inertia_` (sum of squared distances from points to their assigned centroid) for each, and plotted K against inertia.

Inertia values obtained:

| K | Inertia |
|---|---------|
| 1 | 681.37 |
| 2 | 152.35 |
| 3 | 78.86 |
| 4 | 57.35 |
| 5 | 46.47 |
| 6 | 39.07 |
| 7 | 34.31 |

The inertia drops sharply from K=1 to K=3, then flattens out — the "elbow" sits at **K = 3**, which conveniently matches the 3 real Iris species (setosa, versicolor, virginica), even though the model never saw the species labels.

## Insights from the Visualizations

- **Original data (petal length vs petal width), colored by true species** — setosa is clearly separated from the other two species, while versicolor and virginica overlap slightly.
- **K-Means clusters (same features, colored by predicted cluster)** — the clustering closely mirrors the true species groupings. Setosa is separated perfectly; a small number of versicolor and virginica flowers get assigned to the "wrong" cluster due to their overlapping petal measurements.
- **PCA visualization (2 principal components, colored by K-Means cluster)** — the same 3-cluster structure is still clearly visible after compressing from 4 features down to 2, confirming that very little useful information was lost.

**Explained variance ratio:** `[0.7296, 0.2285]`
**Total variance retained:** ~95.8%

This means PC1 alone captures ~73% of the total variance in the original 4 features, and PC2 adds another ~23% — together preserving almost all (95.8%) of the meaningful information while cutting the dimensionality in half.

A cross-tabulation of true species vs K-Means cluster confirmed this numerically: setosa maps to one cluster with zero mixing, while versicolor and virginica show a small amount of overlap between clusters — consistent with what's visible in the scatter plots.

## Files in This Folder

- `dataset_exploration.py` — loading Iris into a Pandas DataFrame and exploring it
- `kmeans_script.py` — K-Means clustering and elbow method
- `pca_script.py` — standardization and PCA
- `mini_project.py` — combined script producing the full comparison visualization
- `elbow_plot.png`
- `kmeans_scatter.png`
- `pca_scatter.png`
- `comparison_plot.png`
- `README.md` — this file




# Day 12 – Introduction to Deep Learning & First ANN

## 📌 Overview
This day marks the start of Phase 2 (Deep Learning) of the MLB Internship. It covers the fundamentals of neural networks — perceptrons, activation functions, and building a first Artificial Neural Network (ANN) — followed by a mini project classifying clothing images using the Fashion MNIST dataset.

---

## 🧠 What is Deep Learning?

Deep Learning is a subfield of Machine Learning based on **Artificial Neural Networks (ANNs)** with multiple layers ("deep" architectures). Instead of relying on manually engineered features, deep learning models automatically learn hierarchical patterns directly from raw data (images, text, audio, etc.) by adjusting internal weights through a process called **backpropagation**.

## ⚖️ Machine Learning vs Deep Learning

| Aspect | Machine Learning | Deep Learning |
|---|---|---|
| Feature engineering | Manual (you design features) | Automatic (network learns features) |
| Data requirement | Works well on smaller datasets | Needs large datasets to perform well |
| Compute requirement | Lower | Higher (benefits from GPU/TPU) |
| Interpretability | Generally more interpretable | Often a "black box" |
| Example algorithms | Logistic Regression, Decision Trees, KNN, SVM | ANN, CNN, RNN, Transformers |

## 🌍 Applications of Deep Learning
- Image classification & object detection
- Computer vision (face recognition, medical imaging)
- Natural Language Processing (translation, chatbots, sentiment analysis)
- Speech recognition
- Recommendation systems
- Autonomous vehicles

## 🏗️ Artificial Neural Networks (ANN)

An ANN is composed of layers of interconnected neurons, loosely inspired by the structure of the human brain:

- **Input Layer** – receives the raw data (e.g., pixel values of an image). It doesn't perform computation; it just defines the shape of the incoming data.
- **Hidden Layer(s)** – perform weighted computations on the inputs and apply an activation function to learn complex, non-linear patterns.
- **Output Layer** – produces the final prediction (e.g., class probabilities for classification tasks).

Each connection between neurons has a **weight**, and each neuron has a **bias** — these are the parameters the network learns during training.

## ⚡ What is a Perceptron?

A perceptron is the simplest unit of a neural network — a single neuron that:
1. Takes one or more inputs
2. Multiplies each input by a weight and sums them, adding a bias
3. Passes that sum through an **activation function** to produce an output

It was the original building block used for simple binary classification, and multiple perceptrons stacked in layers form a full ANN (technically called a Multi-Layer Perceptron, or MLP).

## 🔥 Activation Functions Explored

Activation functions introduce **non-linearity** into the network — without them, a neural network (no matter how many layers) would behave like a single linear model and couldn't learn complex patterns.

| Activation | Range | Commonly Used In |
|---|---|---|
| **ReLU** (Rectified Linear Unit) | 0 to ∞ | Hidden layers of most modern networks — fast, avoids vanishing gradient for positive values |
| **Sigmoid** | 0 to 1 | Output layer of binary classification problems |
| **Tanh** | -1 to 1 | Hidden layers, especially in RNNs — zero-centered output |
| **Softmax** | 0 to 1 (sums to 1 across outputs) | Output layer of multi-class classification problems |

**Why they matter:** Activation functions don't change the number of parameters in a layer — they only change the mathematical transformation applied to each neuron's weighted sum, which determines how the network expresses non-linear relationships in the data.

---

## 🧪 Coding Practice Summary

- **Practice 1:** Installed and verified TensorFlow/Keras in an isolated `uv`-managed Python 3.12 virtual environment (required since TensorFlow doesn't yet support Python 3.14).
- **Practice 2:** Built a simple ANN (Input → Hidden Dense(128, ReLU) → Output Dense(10, Softmax)) and inspected `model.summary()`, including how parameter counts are calculated: `(inputs × neurons) + neurons` per Dense layer.
- **Practice 3:** Compared ReLU, Sigmoid, and Tanh activations in the hidden layer — confirmed that total parameter count stays identical (101,770) across all three, since activation functions only affect the per-neuron math, not the number of weights/biases.

---

## 🖼️ Mini Project: Fashion MNIST ANN

**Dataset:** Fashion MNIST (60,000 training images, 10,000 test images, 28×28 grayscale, 10 clothing categories)

**Pipeline:**
1. Loaded the dataset via `tensorflow.keras.datasets.fashion_mnist`
2. Explored shapes, labels, and visualized sample images
3. Normalized pixel values from [0, 255] to [0, 1]
4. Built an ANN: `Flatten → Dense(128, ReLU) → Dense(10, Softmax)`
5. Compiled with Adam optimizer and sparse categorical crossentropy loss
6. Trained for 10 epochs with a 20% validation split
7. Evaluated on the held-out test set
8. Plotted training/validation accuracy curves
9. Displayed sample predictions vs actual labels

### 📊 Results

| Metric | Value |
|---|---|
| Final Training Accuracy | _fill in from your `history.history['accuracy'][-1]`_ |
| Final Validation Accuracy | _fill in from your `history.history['val_accuracy'][-1]`_ |
| Test Accuracy | _fill in from `test_accuracy` printed output_ |
| Test Loss | _fill in from `test_loss` printed output_ |

*(Replace the placeholders above with the actual numbers from your terminal output once training completes.)*

---

## 📂 Files in this Folder
- `practice1_verify.py` – TensorFlow/Keras installation verification
- `practice2_ann.py` – Simple ANN architecture + model summary
- `practice3_activations.py` – Activation function comparison
- `Mini Project.py` – Full Fashion MNIST ANN pipeline
- `sample_images.png` – Sample dataset images with labels
- Training accuracy graph (add after plotting)
- Sample prediction images (add after prediction step)

---

## ✅ Key Takeaways
- Deep learning automates feature learning through layered neural networks, unlike traditional ML which relies on manual feature engineering.
- A perceptron is the fundamental computational unit of a neural network.
- Activation functions are essential for enabling networks to learn non-linear, complex patterns.
- Even a simple ANN (no CNN) can achieve strong accuracy on Fashion MNIST, since the dataset is relatively low-resolution and well-structured.


# Day 13 — Convolutional Neural Networks (CNNs) & Fashion MNIST Classifier

## Overview

This folder contains the Day 13 deliverables for the MLB Internship: CNN practice exercises and a full Fashion MNIST image classifier built with TensorFlow/Keras.

## Contents

| File | Description |
|---|---|
| `Practice1.py` | Loads Fashion MNIST, visualizes 10 sample images, normalizes pixel values |
| `Practice2_CNN.py` | Builds and trains a CNN (Conv → Pool → Flatten → Dense → Output) |
| `Practice3.py` | Evaluates the trained model, shows sample predictions |
| `fashion_mnist_classifier.py` | Full mini project: training, evaluation, accuracy/loss curves, confusion matrix, correct/incorrect prediction grids |
| `app.py` | Streamlit app for interactive classification |
| `mp_accuracy_loss_curves.png` | Training vs validation accuracy and loss |
| `mp_confusion_matrix.png` | Confusion matrix across all 10 classes |
| `mp_correct_predictions.png` | 10 correctly classified sample images |
| `mp_incorrect_predictions.png` | 10 incorrectly classified sample images |

## Why CNNs are better than ANNs for image data

A plain ANN flattens an image into a 1D vector before the network sees it, which throws away spatial relationships between nearby pixels (e.g. that an eye sits next to a nose). It also needs a separate weight for every pixel-to-neuron connection, which becomes huge and inefficient as image size grows.

CNNs instead slide small filters across the image, preserving 2D spatial structure and reusing the same filter weights at every position. This gives them far fewer parameters, built-in translation invariance, and the ability to learn a hierarchy of features — edges in early layers, shapes and textures in deeper layers, and full object parts by the end.

## Purpose of convolution and pooling layers

- **Convolution layer**: applies learnable filters (kernels) that slide over the image and compute a dot product at each position, producing a feature map that highlights where a particular pattern (edge, curve, texture) appears.
- **Pooling layer**: downsamples feature maps (e.g. max pooling takes the strongest activation in each small region), reducing spatial size and computation while keeping the most important signal and adding some robustness to small shifts in the image.

## Model architecture

```
Input (28x28x1)
 → Conv2D (32 filters, 3x3, ReLU)
 → MaxPooling2D (2x2)
 → Conv2D (64 filters, 3x3, ReLU)
 → MaxPooling2D (2x2)
 → Flatten
 → Dense (128, ReLU)
 → Dense (10, Softmax)
```

Compiled with:
- Optimizer: Adam
- Loss: Sparse categorical crossentropy
- Metric: Accuracy
- Trained for 10 epochs, batch size 32, with a 20% validation split

## Results

*(Fill in with your actual numbers after running `fashion_mnist_classifier.py`)*

- **Training accuracy**: `__.__%`
- **Test accuracy**: `__.__%`
- **Test loss**: `__.__`

**Training vs validation accuracy/loss:**

![Accuracy and loss curves](mp_accuracy_loss_curves.png)

**Confusion matrix:**

![Confusion matrix](mp_confusion_matrix.png)

**Correctly classified samples:**

![Correct predictions](mp_correct_predictions.png)

**Incorrectly classified samples:**

![Incorrect predictions](mp_incorrect_predictions.png)

## Challenges faced

*(Fill in based on what you actually ran into — a few from today's session to start from:)*

- TensorFlow has no wheels for Python 3.14 yet, so the `.venv` had to be pinned to Python 3.12 with `uv venv --python 3.12`.
- An empty `Practice2_CNN.py` file caused a silent no-op run — fixed by re-saving the script and using `python -u` to force unbuffered output for visibility during training.

## Links

- **GitHub repository**: `<add link>`
- **Streamlit app / Hugging Face Space**: `<add link>`



# Day 15 — Introduction to Object Detection (YOLO)

## What is Object Detection?

Object detection is a computer vision task that identifies **what** objects are present in an image and **where** they are located. Unlike simpler vision tasks, it doesn't just describe the image as a whole — it draws a bounding box around each object instance and assigns it a class label along with a confidence score (how sure the model is about that prediction).

## How is it different from Image Classification?

Image classification predicts a single label for an entire image (e.g. "this image contains a dog"). Object detection goes further — it can find **multiple** objects in a single image, tell you exactly where each one is (via a bounding box), and label each one independently. So a single photo could return "2 persons, 1 car, 1 dog" instead of just one label for the whole frame.

## What is YOLO?

YOLO (You Only Look Once) is a family of object detection models that process an entire image in a single forward pass through a neural network, predicting all bounding boxes, class labels, and confidence scores at once. This is what makes YOLO fast enough for real-time detection (video, webcam feeds), unlike older approaches that scanned an image region-by-region. For this task, the pretrained **YOLOv8n** model (Ultralytics) was used, trained on the COCO dataset (80 everyday object classes).

## Dataset Used

**Drone Detection Computer Vision Model** (Roboflow Universe)
- 312 images
- 3 classes: `Bird`, `Drone`, `Plane`
- Downloaded in YOLO format (train/valid/test splits with images + YOLO-format label files)

Link: https://universe.roboflow.com/drone-detection-i4yej/drone-detection-lzvig

## What objects were detected?

Since the pretrained YOLOv8n model was trained only on COCO's 80 classes, and **"Drone" is not one of them**, the model could not directly recognize drones as their own class. Running inference on 10 sample test images produced the following pattern:

| Outcome | Frequency |
|---|---|
| Detected but mislabeled as **airplane** | 2 images |
| Detected but mislabeled as other COCO classes (person, bird, frisbee, train) | 3 images |
| No detection at all | 4 images |
| Multiple unrelated objects detected in a busy scene | 1 image |

## Observations

The pretrained YOLOv8n model was able to correctly **localize** several drones (i.e. draw a bounding box roughly around the object) but consistently **mislabeled** them — most often as "airplane," since drones and airplanes share a broadly similar silhouette (elongated body, protruding arms/wings) from a distance. Some drones, particularly smaller or more distant ones, went undetected entirely — likely because their visual features didn't cross the model's confidence threshold for any of its known classes.

This is a clear demonstration of a core limitation of off-the-shelf pretrained models: general object *localization* ability transfers well to new domains, but class-specific *recognition* does not. The model can tell "something is there" but doesn't know its name unless it was trained on that exact class. This is the direct motivation for fine-tuning / custom training (covered in the next session), where the same pretrained COCO weights would be used as a starting point and further trained on the labeled drone dataset so the model learns to recognize "Drone" as its own class.

## Deliverables

- `practice1.py` — YOLOv8 basic inference practice (single image + multiple images)
- `practice2.py` — Inference on custom/own images
- `run_inference.py` — Inference on the drone dataset test images
- `download_dataset.py` — Roboflow dataset download script
- `app.py` — Streamlit app for image/video upload, detection, and result download
- `Drone-detection-4/` — Dataset (train/valid/test, YOLO format)
- `drone_output_*.jpg` — Sample output images with detections
- `output_single.jpg`, `output_0.jpg`, `output_1.jpg` — Practice outputs

## Submission

1. GitHub repo link: _add link here_
2. Streamlit app: run locally via `uv run streamlit run app.py`



# Image Processing Toolkit

A menu-driven image processing toolkit built with **Python** and **OpenCV**, available in two versions:

- `image_toolkit.py` — a console/terminal menu-driven app
- `app.py` + `image_ops.py` — a Streamlit web app version

Both support: loading an image, grayscale conversion, resize, rotate, flip, crop, drawing shapes, adding text, saving/downloading the result, plus bonus features (brightness/contrast adjustment, BGR vs RGB comparison, and side-by-side original vs processed display).

---

## BGR vs RGB

Most people think of colors in **RGB** order — Red, Green, Blue. OpenCV does it backwards and uses **BGR** — Blue, Green, Red.

Same pixel data, different order. If you display it with the wrong order in mind, the colors come out swapped (usually red and blue look flipped).

This shows up a few times in the project:

- OpenCV itself (reading, saving, drawing, `cv2.imshow()`) always uses BGR.
- Streamlit's `st.image()` expects RGB, so images need converting with `cv2.cvtColor(image, cv2.COLOR_BGR2RGB)` before display.
- Streamlit's color picker gives colors in RGB, so they need reordering into `(B, G, R)` before OpenCV can draw with them correctly.

The bonus feature shows both versions of the same image side by side so the difference is easy to see.

---

## What are grayscale images, and why use them?

A color image has 3 channels (Blue, Green, Red) per pixel. A **grayscale** image has just 1 — a single brightness value from 0 (black) to 255 (white), with no color at all.

Why use it:

- **Faster to process** — one channel instead of three.
- **Color isn't always needed** — things like edge detection or face detection usually just care about shapes and brightness, not color.
- **Cleaner for some tasks** — removing color can make edges and patterns easier to pick out.

In `image_ops.py`, `to_grayscale()` first converts with `cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)`, then converts it back to a 3-channel image with `COLOR_GRAY2BGR`. It still looks grayscale, but this keeps the array shape consistent so drawing, adding text, or saving still work fine afterward.

---

## OpenCV functions used

| Function | Purpose |
|---|---|
| `cv2.imread()` | Load an image from disk (as color or grayscale) |
| `cv2.imwrite()` | Save an image to disk |
| `cv2.imencode()` | Encode an image to bytes in memory (used for Streamlit's download button, instead of writing to disk first) |
| `cv2.imdecode()` | Decode raw bytes (e.g. an uploaded file) back into an OpenCV image |
| `cv2.cvtColor()` | Convert between color spaces (BGR ↔ RGB, BGR ↔ Grayscale) |
| `cv2.resize()` | Resize an image, either to exact dimensions or by a scale factor (`fx`, `fy`) |
| `cv2.rotate()` | Fast 90°/180°/270° rotation |
| `cv2.getRotationMatrix2D()` + `cv2.warpAffine()` | Rotate by an arbitrary angle |
| `cv2.flip()` | Flip horizontally, vertically, or both |
| NumPy slicing (`image[y1:y2, x1:x2]`) | Crop to a region of interest (OpenCV has no dedicated crop function — cropping is just array slicing) |
| `cv2.rectangle()`, `cv2.line()`, `cv2.circle()`, `cv2.polylines()` | Draw shapes with customizable color and thickness |
| `cv2.putText()` | Add custom text with a chosen font, size, color, and thickness |
| `cv2.convertScaleAbs()` | Adjust brightness/contrast (`alpha` scales for contrast, `beta` shifts for brightness), with built-in clipping to the valid 0–255 range |
| `cv2.imshow()`, `cv2.waitKey()`, `cv2.destroyAllWindows()` | Display images and manage window lifecycle (console version only) |
| `np.hstack()` | Stack two images side by side for comparison views |

---

## Challenges faced and how they were solved

**1. Grayscale broke other operations.**
A grayscale image has only 1 channel, but drawing and saving expected 3. Fixed by converting it back to a 3-channel image right after graying it out, so it still looks grayscale but works with everything else.

**2. Crop coordinates going out of range.**
Typing in coordinates that were too big, or in the wrong order, gave an empty or broken crop. Fixed by clamping all values to the image's actual size and sorting them before slicing.

**3. Colors looking wrong in Streamlit.**
OpenCV uses BGR, but Streamlit's image display and color picker both use RGB — so colors would show up swapped. Fixed by converting to RGB before displaying, and converting picked colors back to BGR before drawing with them.

**4. Streamlit app not opening.**
Running `uv run app.py` just executed the file as plain Python instead of starting the app. Fixed by running it the right way: `uv run streamlit run app.py`.

**5. Saving without a file extension.**
`cv2.imwrite()` needs a file extension (like `.png`) to know what format to save in — a name like `New_image` with no extension caused an error. Fixed by always including one when saving.

**6. Keeping undo simple.**
Every processing function returns a brand new image instead of editing the original in place. That way each step can be stored separately, making undo easy to add later without extra rework.


# Day 17 — Image Processing & Document Enhancement


Most of the tasks logic is implemented in the code itself.

## What is Image Processing?

Image processing is the process of using computer algorithms to modify, analyze, or enhance digital images. In this project, **Python**, **OpenCV**, and **NumPy** are used to perform common image transformations and enhancement operations.

The project focuses on two main areas:

- Learning fundamental OpenCV transformations and filters.
- Building a **Document Image Enhancement Tool** that automatically improves the quality of document images.

A **Streamlit app** was also created to make the image-processing operations interactive through a web interface.

---

# Image Transformations

The coding practice section implements the following transformations:

## 1. Translation

Translation moves an image horizontally and vertically.

The transformation is performed using an affine transformation matrix:

```python
matrix = np.float32([
    [1, 0, tx],
    [0, 1, ty]
])

and applied using:

cv2.warpAffine()

The values tx and ty determine how far the image is moved along the x and y axes.

Purpose

Translation is useful for repositioning an image without changing its size, rotation, or shape.

2. Rotation

Rotation changes the orientation of an image around a selected center point.

The project uses:

cv2.getRotationMatrix2D()

followed by:

cv2.warpAffine()

The rotation function demonstrates a 45-degree rotation.

Purpose

Rotation is useful for correcting images that are tilted or changing the orientation of an image.

3. Scaling

Scaling changes the size of an image.

The project uses:

cv2.resize()

Two scaling operations are demonstrated:

Scaling an image up.
Scaling an image down.

Different interpolation methods are used depending on the direction of the scaling.

Purpose

Scaling is useful for resizing images while maintaining their visual content.

4. Affine Transformation

Affine transformation maps three points from an original image to three new points.

The project uses:

cv2.getAffineTransform()

and:

cv2.warpAffine()
Purpose

Affine transformation can be used to translate, rotate, scale, and shear an image while preserving straight lines.

5. Perspective Transformation

Perspective transformation maps four points from an original image to four points in a destination image.

The project uses:

cv2.getPerspectiveTransform()

and:

cv2.warpPerspective()
Purpose

Perspective transformation is especially useful for correcting photographs of documents taken from an angle.

It changes the geometry of the image so that a tilted document can be transformed into a rectangular, front-facing document.

Image Enhancement Techniques

The main project is a Document Image Enhancement Tool.

The processing pipeline is:

Input Document
      ↓
Document Contour Detection
      ↓
Perspective Correction
      ↓
Grayscale Conversion
      ↓
Noise Reduction
      ↓
Brightness & Contrast Adjustment
      ↓
Sharpening
      ↓
Enhanced Document

Each step has a specific purpose.

Document Contour Detection

The application attempts to automatically find the document in the image.

The image is first converted to grayscale and blurred:

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

Canny edge detection is then applied:

edged = cv2.Canny(blurred, 50, 150)

Contours are detected and the program searches for a large four-sided contour.

Purpose

The purpose of contour detection is to automatically find the four corners of a document so that perspective correction can be performed without manually selecting the points.

Perspective Correction

Once a four-point document contour is detected, the points are ordered as:

Top Left
Top Right
Bottom Right
Bottom Left

The points are then mapped to a rectangular output using:

cv2.getPerspectiveTransform()

and:

cv2.warpPerspective()
Purpose

Perspective correction straightens a tilted document and makes it appear more like a scanned page.

This was the enhancement step that produced the biggest visual improvement on tilted documents because it corrects the overall geometry of the page before the other enhancement techniques are applied.

Grayscale Conversion

The perspective-corrected image is converted to grayscale using:

cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
Purpose

Grayscale removes color information and reduces the image to a single brightness channel.

For document images, color is usually less important than the contrast between the text and the background.

Grayscale also makes later processing simpler and faster.

Noise Reduction

The document enhancement pipeline uses a bilateral filter:

cv2.bilateralFilter(
    img,
    d=9,
    sigmaColor=75,
    sigmaSpace=75
)
Purpose

Noise reduction removes unwanted small variations and artifacts from the image.

A bilateral filter was selected because it reduces noise while preserving important edges such as text boundaries.

Brightness Enhancement

Brightness and contrast are adjusted using:

cv2.convertScaleAbs(
    img,
    alpha=1.3,
    beta=15
)

Here:

alpha controls contrast.
beta controls brightness.
Purpose

Brightness adjustment helps improve documents that are too dark or have uneven lighting.

Contrast Enhancement

The same cv2.convertScaleAbs() operation is used to increase the contrast of the document.

cv2.convertScaleAbs(
    img,
    alpha=1.3,
    beta=15
)
Purpose

Increasing contrast makes the difference between the document background and the text more noticeable.

This can improve readability, especially when the original photograph is low contrast.

Sharpening

The final image is sharpened using a convolution kernel:

kernel = np.array([
    [0, -1, 0],
    [-1, 5, -1],
    [0, -1, 0]
])

sharpened = cv2.filter2D(img, -1, kernel)
Purpose

Sharpening makes edges more defined.

For document images, this can make letters and other small details appear clearer after resizing, filtering, and perspective correction.

Blurring Techniques

The coding practice section also implements three different blur techniques.

Gaussian Blur
cv2.GaussianBlur()

Gaussian blur smooths an image and reduces high-frequency noise.

It can also be useful as a preprocessing step before edge detection.

Median Blur
cv2.medianBlur()

Median blur replaces pixels with the median value of their surrounding neighborhood.

It is useful for reducing certain types of noise while preserving edges reasonably well.

Bilateral Filter
cv2.bilateralFilter()

Bilateral filtering smooths an image while preserving edges.

This is particularly useful for document enhancement because text edges should remain visible while unwanted noise is reduced.

Brightness and Contrast

The project demonstrates both increasing and decreasing brightness and contrast.

Brightness is controlled using the beta parameter:

cv2.convertScaleAbs(image, alpha=1.0, beta=50)

Contrast is controlled using the alpha parameter:

cv2.convertScaleAbs(image, alpha=1.5, beta=0)

In general:

alpha > 1 → higher contrast
alpha < 1 → lower contrast
beta > 0 → brighter image
beta < 0 → darker image
OpenCV Functions Used
Function	Purpose
cv2.imread()	Loads an image from disk
cv2.imwrite()	Saves an image to disk
cv2.cvtColor()	Converts between color spaces such as BGR and grayscale
cv2.resize()	Resizes an image
cv2.getRotationMatrix2D()	Creates a rotation matrix
cv2.warpAffine()	Applies an affine transformation
cv2.getAffineTransform()	Creates an affine transformation matrix from three point pairs
cv2.getPerspectiveTransform()	Creates a perspective transformation matrix from four point pairs
cv2.warpPerspective()	Applies a perspective transformation
cv2.GaussianBlur()	Applies Gaussian blur
cv2.medianBlur()	Applies median blur
cv2.bilateralFilter()	Reduces noise while preserving edges
cv2.Canny()	Detects edges
cv2.findContours()	Finds contours in an image
cv2.contourArea()	Calculates the area of a contour
cv2.approxPolyDP()	Approximates a contour with fewer points
cv2.convertScaleAbs()	Adjusts brightness and contrast
cv2.filter2D()	Applies a custom convolution filter
np.float32()	Creates NumPy arrays with the required floating-point type
np.hstack()	Combines images horizontally for comparison
Challenge Task — Five Tilted Documents

The mandatory challenge requires five tilted document images to be processed using the document enhancement tool.

For each document, the application saves:

Original image
Perspective-corrected image
Final enhanced image
Side-by-side comparison image

The comparison image makes it easier to see how the document changes throughout the processing pipeline.

The five challenge images are:

image1.jpg
image2.jpg
image3.jpg
image4.jpg
image5.jpg

The challenge demonstrates that the same document enhancement pipeline can be applied to multiple tilted documents.

Which Transformation Had the Biggest Impact?

The perspective transformation had the biggest impact on document quality, especially for the tilted document challenge.

A document photographed from an angle does not appear as a normal rectangle. Its corners and edges are distorted because of the camera's perspective.

Perspective correction fixes this geometry by mapping the detected four document corners to a rectangular output.

This produced the most noticeable improvement because it changed the overall shape and orientation of the document.

The other enhancement techniques then improved the corrected image further:

Perspective Correction
        ↓
Grayscale
        ↓
Noise Reduction
        ↓
Brightness / Contrast
        ↓
Sharpening

Therefore, perspective correction had the biggest visual impact, while the complete pipeline produced the best final result.

Challenges Faced and How They Were Solved

1. Automatically detecting the document.

Finding the document boundary automatically was one of the main challenges. The program uses Canny edge detection followed by contour detection and searches for a large four-sided contour. If no suitable contour is found, the program falls back to using the original image instead of failing.

2. Ordering the document corners correctly.

Perspective transformation requires the four corners to be in the correct order. A custom order_points() function was implemented to arrange the points as top-left, top-right, bottom-right, and bottom-left before applying the transformation.

3. Handling tilted documents.

A tilted document can have significantly different corner positions depending on the camera angle. The automatic contour detection and perspective transformation were combined to handle these cases without manually entering the corner coordinates.

4. Grayscale images having one channel.

The original images are normally three-channel BGR images, while grayscale images contain only one channel. This caused an issue when creating side-by-side comparison images. A helper function was used to convert grayscale images into three-channel images before combining them.

5. Handling file paths.

The project contains folders with spaces such as Input images, Output images, and Mini Project. Relative paths and os.path.join() were used to make file handling more reliable.

6. Processing multiple image formats.

The program supports common image formats including .jpg, .jpeg, and .png. The input directory is scanned and only supported image files are processed.

7. Converting the OpenCV project into a Streamlit application.

The original practice programs used cv2.imshow(), cv2.waitKey(), and terminal input. These are not suitable for a browser-based interface, so the Streamlit version uses file uploaders, buttons, sliders, image previews, and download buttons instead.

8. Running Streamlit correctly.

Running:

uv run app.py

only executes the Python file normally. The Streamlit application must instead be started with:

uv run streamlit run app.py
Streamlit Application

A Streamlit web application was created to provide an interactive interface for the image-processing operations.

The application allows the user to upload an image and select different operations.

Available operations include:

Document Enhancement
Translation
Rotation
Scaling
Affine Transformation
Perspective Transformation
Brightness Adjustment
Contrast Adjustment
Gaussian Blur
Median Blur
Bilateral Filter
Sharpening

The processed image can be viewed directly in the browser and downloaded after processing.

Deliverables
Mini_Project.py — Document image enhancement tool and challenge task
app.py — Streamlit application for interactive image processing
practice.py — OpenCV coding practice for transformations and enhancement techniques
Input images/ — Input image dataset
Output images/ — Enhanced and processed output images
challenge_task/ — Challenge outputs containing original, corrected, enhanced, and comparison images
README.md — Project documentation
pyproject.toml — Project dependencies and configuration
Technologies Used
Python
OpenCV
NumPy
Streamlit
Running the Project
Run the Python Document Enhancement Tool

From the project directory:

uv run python Mini_Project.py

The program loads the images, processes them, and saves the enhanced results.

Run the Streamlit Application

Start the web application with:

uv run streamlit run app.py

The application can then be opened in a web browser.

Project Structure
Day17/
│
├── Input images/
│   ├── image1.jpg
│   ├── image2.jpg
│   ├── image3.jpg
│   ├── image4.jpg
│   ├── image5.jpg
│   ├── image6.jpg
│   ├── image7.jpg
│   ├── image8.jpg
│   ├── image9.jpg
│   └── image10.jpg
│
├── Output images/
│
├── Mini Project/
│   └── Images/
│       ├── Mini_Project.py
│       ├── image1.jpg
│       ├── image2.jpg
│       ├── image3.jpg
│       ├── image4.jpg
│       ├── image5.jpg
│       └── challenge_task/
│
├── app.py
├── practice.py
├── pyproject.toml
└── README.md
Submission
GitHub repo link: add link here
Streamlit app: run locally via uv run streamlit run app.py
Document enhancement tool: Mini_Project.py
Five tilted document challenge outputs: challenge_task/

# Day 18 — Edge Detection, Morphology & Document Boundary Detection

## 1. Sobel vs Laplacian vs Canny

| Method | How it works | Characteristics |
|---|---|---|
| **Sobel** | 1st-order derivative; separate Gx/Gy kernels combined into gradient magnitude | Directional, somewhat noise-resistant (built-in smoothing), produces thick edges |
| **Laplacian** | 2nd-order derivative; single isotropic kernel, detects zero-crossings | Direction-independent, very noise-sensitive, tends to produce double edges |
| **Canny** | Multi-stage pipeline: Gaussian blur → Sobel gradients → non-max suppression → double-threshold hysteresis | Thin, clean, well-connected single-pixel edges — most robust of the three, used for the boundary detection tool |

## 2. Morphological Operations — Purpose

- **Erosion**: shrinks white regions, removes small noise, thins objects
- **Dilation**: grows white regions, fills small gaps, thickens objects
- **Opening** (erode→dilate): removes small noise while preserving overall object size
- **Closing** (dilate→erode): fills small holes/gaps, bridges broken edges — critical for turning a broken Canny outline into one continuous boundary
- **Morphological Gradient** (dilate−erode): extracts object outline/edge from a binary shape
- **Top Hat** (original−opening): highlights small bright details on a dark background
- **Black Hat** (closing−original): highlights small dark details on a light background

## 3. Best-Performing Combination

**Pipeline**: Grayscale → Gaussian Blur `(15,15)` → Canny `(30, 100)` → Morphological Closing `(9,9)`, 2 iterations → contour filtering (area + solidity + 4-point approximation) → draw boundary.

**Parameters tuned and why:**
- **Gaussian blur kernel**: started at `(5,5)`, increased to `(15,15)`. Small kernels left fine text edges intact, which Canny then falsely detected as strong edges, competing with the real document boundary during contour selection.
- **Canny thresholds**: started at `(50,150)`, loosened to `(30,100)`. Lower thresholds were needed after heavier blurring reduced the boundary's edge contrast, so weaker gradients along the true edge still get picked up.
- **Closing kernel**: increased from `(5,5)` to `(9,9)`, 2 iterations, to bridge gaps in the boundary caused by shadows/low contrast without over-merging unrelated regions.
- **Contour selection logic**: rather than blindly taking the largest contour, added an **area filter** (discard anything under ~10% of image area), a **solidity filter** (`area / convex_hull_area > 0.85`, to reject jagged text blobs that pass the area check but aren't shape-like a document), and a **4-point `approxPolyDP`** check (epsilon = `0.02 × perimeter`) to isolate a clean quadrilateral.
- Also tried: bilateral filtering (didn't help — it preserves high-contrast text edges by design) and a large morphological closing directly on grayscale to erase text before edge detection (helped a few images but oversized/undersized inconsistently due to varying text scale across photos — informed the resize-normalization step).
- **Resize normalization**: added a fixed-width resize (`800px`) on load so kernel sizes behave consistently across images with different original resolutions/zoom levels.

## 4. Challenges Faced

- **Text vs. boundary confusion**: dense receipt text produces strong, high-contrast edges that Canny detects just as readily as the actual document boundary. On several images, `findContours` picked the largest connected *text blob* instead of the receipt outline, even after area and shape filtering.
- **Low contrast backgrounds**: images with the receipt against light-colored or busy backgrounds (siding, tray, table) had a genuinely faint boundary edge, making it hard for Canny to capture a continuous outline even after tuning.
- **Scale inconsistency across the dataset**: images varied significantly in resolution and zoom, so a single fixed kernel size didn't generalize — a kernel that removed text in one image was too small (or too large) in another.
- **Steep tilt / partial frame**: a few images (folded receipts, steep camera angles, receipt edges nearly parallel to the camera) pushed past what a classical Canny + contour pipeline can reliably solve without a trained segmentation model — these are documented as known limitations rather than forced to a false positive.

Out of 15 test images, the tuned pipeline correctly detects the document boundary on the majority; the remaining failures are consistent with the challenges above (dense text merging, low contrast, extreme tilt).

# Day 19 — Contours in OpenCV & Shape Detection System

## Overview

Today's focus was moving from pixel-level image processing (Days 16–18) into **structural** image analysis — finding, measuring, and classifying the actual objects inside an image using contours. The deliverable is a full Shape Detection System that can load an image, detect every shape present, label it, and report its geometric properties.

## What Are Contours?

A contour is a curve joining all continuous points along a boundary that share the same intensity — in practice, it's the outline of an object. OpenCV finds contours by tracing the border between foreground and background regions in a **binary** (black-and-white only) image. It has no understanding of what a shape "is" — it's a purely topological trace of where pixel values change from one region to another, which is why every contour pipeline starts by converting the image into a clean binary map first (via thresholding or edge detection) before any shape can be found at all.

## How Contour Detection Works

The pipeline follows a fixed order, where each step depends on the one before it:

1. **Convert to binary** — `cv2.threshold()` (or Canny edge detection) collapses the image down to pure black/white, since contour tracing can't work on ambiguous grayscale values.
2. **Find contours** — `cv2.findContours()` walks the binary image and returns every closed boundary it finds as a list of points.
3. **Filter noise** — small stray contours (JPEG artifacts, thresholding noise) get discarded by area, since `findContours` returns everything, significant or not, with no judgment of its own.
4. **Measure each contour**:
   - `cv2.contourArea()` — enclosed area (Shoelace formula)
   - `cv2.arcLength()` — perimeter, by summing the distance between every consecutive boundary point
   - `cv2.boundingRect()` — smallest upright rectangle containing the shape
   - `cv2.minEnclosingCircle()` — smallest circle containing the shape
5. **Approximate the shape** — `cv2.approxPolyDP()` reduces a noisy, many-point contour down to just its corner points, which is what makes vertex-counting possible.
6. **Classify** — vertex count, aspect ratio (for square vs. rectangle), and circularity (`4π·Area / Perimeter²`, which is 1.0 for a perfect circle) together determine the shape label.
7. **Draw & save** — contour outline, bounding rect, label, and area/perimeter text get drawn onto the output image, which is then written to disk.

## Shapes the Program Can Detect

- Triangle
- Square
- Rectangle
- Pentagon
- Hexagon
- Heptagon
- Octagon
- Nonagon
- Circle
- Polygon (fallback for anything else with more vertices)

Classification is purely geometric — no machine learning involved. Vertex count from `approxPolyDP` picks the base category, aspect ratio disambiguates square from rectangle, and circularity catches genuinely round shapes that would otherwise get approximated into a high-vertex polygon.

## Project Structure

```
Day-19/
├── contour_practice.py    # Core contour detection & measurement script
├── main.py                 # Shape Detection System (full pipeline + classifier)
├── Input images/            # 13 test images (colored fills, outlines, multiple polygon types)
├── Output images/            # original / contours / final-labeled trio per input image
├── pyproject.toml / uv.lock  # dependency management via uv
└── README.md
```

## How to Run

```bash
uv run main.py
```

Processes every image in `Input images/` and saves three outputs per image into `Output images/`:
`<name>_original.jpg`, `<name>_contours.jpg`, `<name>_final.jpg`.

## Challenges Faced

**Grayscale conversion hides colors unevenly.** OpenCV's grayscale conversion uses a luminance-weighted formula (`0.299R + 0.587G + 0.114B`), which meant on colored shapes against a black background, yellow came through bright enough to threshold cleanly, but blue and red barely registered at all — they were nearly as dark as the background itself. The result: only part of a multi-colored image (e.g. one quadrant of a ring split into red/green/blue/yellow segments) was ever detected. Fixed by thresholding on the **max value across B, G, R channels** instead of the weighted grayscale average, so any channel being "lit up" counts as foreground regardless of hue.

**One threshold strategy doesn't fit the whole dataset.** The dataset mixes filled colored shapes on black backgrounds with plain black-outline shapes on white backgrounds — these need opposite thresholding logic (bright-foreground vs. dark-foreground). A single fixed `THRESH_BINARY` call misclassified outlined shapes entirely: the thin outline became a "hole" inside a solid white region, `RETR_EXTERNAL` ignored the interior boundary, and the contour that survived was the outer edge of the whole white canvas — a 4-sided shape that got labeled "Rectangle" no matter what was actually drawn. Fixed by sampling the image's corner pixels to estimate background brightness first, then branching between inverted and non-inverted thresholding depending on whether the background is light or dark.

**Polygon vertex approximation is epsilon-sensitive.** Higher-vertex shapes (heptagon, hexagon, nonagon) are the most fragile to classify correctly — if `approxPolyDP`'s epsilon is too aggressive relative to the shape's perimeter, adjacent vertices merge and the vertex count drops, misclassifying (e.g.) a heptagon as a hexagon. Kept epsilon proportional to perimeter (`0.02 × arcLength`) rather than a fixed pixel value, so it scales correctly across differently-sized shapes.

**Circle vs. many-sided polygon ambiguity.** A circle approximated by `approxPolyDP` at low epsilon can land anywhere from 8 to 20+ vertices, which would otherwise get misread as "Polygon." Resolved by checking circularity (`4π·Area / Perimeter²`) alongside vertex count — anything sufficiently round gets classified as a circle regardless of how many approximation points it produced.

## 📌 Notes
More days and topics will be added here as the internship progresses.
