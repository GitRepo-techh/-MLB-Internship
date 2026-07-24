import pandas as pd



# Pandas

# 1. Using any sample CSV dataset (Students, Sales, or Titanic):
# 2. Load the dataset.
# 3. Display the first and last five rows.
# 4. Display dataset information.
# 5. Find missing values.
# 6. Filter data based on a condition.
# 7. Calculate summary statistics.

# 1, 2, 3, 4 , 5 & 7:

df = pd.read_csv("Day6/student_performance.csv")
print(df.head(1))         # indexing also starts from 0 
print(df.tail())          # prints the last 5 rows 
print(df.info())          # displays dataset information
print(df.describe())      # calculates summary statistics
print(df.isnull().sum())  # finds missing values
print(df.shape)           # displays the shape of the dataset
print(df.columns)         # displays the column names

# 6:

filtered_data = df[["Name" , "Python"]]
filter_ml = df[df["Machine_Learning"] >= 85]
filter_Ai = df[(df["Program"] == "AI") & (df["Attendance"] >= 90)]
mean_value = df["Python"].mean()

print(filtered_data)    
print(filter_ml)
print(filter_Ai)
print(mean_value)
print(df.sort_values("Python", ascending = False))
print(df.groupby("Program")["Python"].mean())