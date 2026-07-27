import pandas as pd

ab = pd.read_csv("Day7/student_performance.csv")


print(ab.isnull().sum())
print(ab.dtypes)
print(ab.duplicated().sum())

ab["Average_Score"] = ab[["Python", "Mathematics", "Statistics", "Machine_Learning"]].mean(axis=1)

ab["Performance"] = pd.cut(
    ab["Average_Score"],
    bins=[0, 70, 80, 90, 101],   
    labels=["Needs Improvement", "Average", "Good", "Excellent"],
    right=False
)

print(ab[["Name", "Average_Score", "Performance"]])
print(ab["Performance"].isnull().sum()) 


ab.to_csv("Day7/cleaned_student_performance.csv", index=False)
