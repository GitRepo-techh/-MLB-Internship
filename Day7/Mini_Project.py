import pandas as pd
import matplotlib.pyplot as plt
import os

# load cleaned data (robust path so it works no matter where we run from)
script_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(script_dir, "cleaned_student_performance.csv"))

subjects = ["Python", "Mathematics", "Statistics", "Machine_Learning"]

# 1. Total students
total_students = len(df)
print("Total Students:", total_students)

# 2. Average score per subject
subject_avg = df[subjects].mean()
print("\nAverage Score per Subject:")
print(subject_avg)

# 3. Top 5 students
top5 = df.sort_values(by="Average_Score", ascending=False).head(5)
print("\nTop 5 Students:")
print(top5[["Name", "Average_Score"]])

# 4. Students needing improvement
needs_improvement = df[df["Performance"] == "Needs Improvement"]
print("\nStudents Needing Improvement:")
print(needs_improvement[["Name", "Average_Score"]])

# 5. Subject with highest average
best_subject = subject_avg.idxmax()
print("\nSubject with Highest Average:", best_subject)

# 6. Visualize the results

# Bar chart - average per subject
plt.figure(figsize=(8,6))
plt.bar(subject_avg.index, subject_avg.values, color="orange")
plt.title("Average Score per Subject")
plt.xlabel("Subject")
plt.ylabel("Average Score")
plt.savefig(os.path.join(script_dir, "dashboard_subject_avg.png"))
plt.show()

# Bar chart - top 5 students
plt.figure(figsize=(8,6))
plt.bar(top5["Name"], top5["Average_Score"], color="green")
plt.title("Top 5 Students")
plt.xlabel("Student Name")
plt.ylabel("Average Score")
plt.savefig(os.path.join(script_dir, "dashboard_top5.png"))
plt.show()