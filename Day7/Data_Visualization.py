import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# load the cleaned data
df = pd.read_csv("Day7/cleaned_student_performance.csv")

print(df.head())

# 1. Bar Chart - average score of each student
plt.figure(figsize=(10,6))
plt.bar(df["Name"], df["Average_Score"])
plt.xticks(rotation=90)
plt.xlabel("Student Name")
plt.ylabel("Average Score")
plt.title("Average Score per Student")
plt.savefig("bar_avg_score.png")
plt.show()

# 2. Histogram - distribution of average scores
plt.figure(figsize=(8,6))
plt.hist(df["Average_Score"], bins=10, color="skyblue", edgecolor="black")
plt.xlabel("Average Score")
plt.ylabel("Number of Students")
plt.title("Distribution of Average Scores")
plt.savefig("hist_avg_score.png")
plt.show()

# 3. Scatter Plot - Python marks vs Machine Learning marks
plt.figure(figsize=(8,6))
plt.scatter(df["Python"], df["Machine_Learning"])
plt.xlabel("Python Marks")
plt.ylabel("Machine Learning Marks")
plt.title("Python vs Machine Learning Marks")
plt.savefig("scatter_python_ml.png")
plt.show()

# 4. Pie Chart - performance categories
performance_count = df["Performance"].value_counts()
plt.figure(figsize=(7,7))
plt.pie(performance_count, labels=performance_count.index, autopct="%1.1f%%")
plt.title("Performance Categories")
plt.savefig("pie_performance.png")
plt.show()

# 5. Box Plot - marks in all subjects
subjects = df[["Python", "Mathematics", "Statistics", "Machine_Learning"]]
plt.figure(figsize=(8,6))
sns.boxplot(data=subjects)
plt.title("Marks in Each Subject")
plt.savefig("box_subjects.png")
plt.show()