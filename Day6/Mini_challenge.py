import pandas as pd

# Student Performance Analysis:

# Using a CSV dataset containing student records, perform the following:
# 1. Load the dataset using Pandas.
# 2. Display basic information about the dataset.
# 3. Calculate average marks for each subject.
# 4. Identify the top 5 performing students.
# 5. Find students scoring below the average.
# 6. Display the total number of students.
# 7. Save the cleaned or analyzed dataset as a new CSV file.

# 1:
ab = pd.read_csv("Day6/student_performance.csv")

# 2:
print(ab.info())  # Display basic information about the dataset
print(ab.columns)

# 3:
subject_avg = ab[["Python", "Mathematics", "Statistics", "Machine_Learning"]].mean()  # We pass the coulmns that we want the function to perform and after that the fnction we wan to perform in this case i.e. mean
print(subject_avg)

# 4:
ab["totalmarks"] = ab[["Python", "Mathematics", "Statistics", "Machine_Learning"]].sum(axis = 1)   # This creates a new Column that contains the sum of all the specified subject marks.
# what axis = 1 did here was to read the csv file row by row
print(ab.sort_values("totalmarks", ascending = False).head(5)) # ascending here helped keep the order of the column descending and head(5) printed the top 5 students.

# 5:
average_total_marks = ab["totalmarks"].mean()
print(f"The avearge total marks are {average_total_marks}")
below_average_students = ab[ab["totalmarks"] <= average_total_marks]
print(f"The students that are below average are: \n {below_average_students}")

# 6:
print(f"The total number of students that study here are {len(ab)}")   # As .space gave us no. of rows and columns and total no. of students is equal to the total number of rows

# 7:
ab.to_csv("Analyzed_Students")  # .to_csv saved the changes in a new csv file 




  
