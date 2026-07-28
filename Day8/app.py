import io
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

st.set_page_config(page_title="Student Score Prediction System", layout="wide")
st.title("🎓 Student Score Prediction System")
st.caption("Day 8 Mini Project — Linear Regression with Scikit-learn")

# ---------------------------------------------------------
# Built-in sample dataset (used automatically if no CSV is found
# locally and nothing is uploaded — so the app always has data to
# run on, e.g. when deployed on Streamlit Cloud).
# ---------------------------------------------------------
SAMPLE_CSV = """Student_ID,Name,Age,Program,Python,Mathematics,Statistics,Machine_Learning,Attendance
S001,Ali Khan,20,AI,85,78,92,88,95
S002,Sara Ahmed,21,AI,72,75,70,80,90
S003,Ahmed Raza,22,SE,90,88,91,93,96
S004,Fatima Noor,20,DS,65,70,68,72,85
S005,Usman Ali,21,AI,78,82,80,76,88
S006,Zainab Iqbal,20,SE,60,65,63,68,80
S007,Bilal Hassan,22,DS,88,85,90,91,94
S008,Ayesha Malik,21,AI,55,60,58,62,75
S009,Hassan Sheikh,23,SE,95,92,96,94,98
S010,Mariam Yousaf,20,DS,70,72,74,71,87
S011,Omar Farooq,21,AI,82,80,85,84,92
S012,Hina Tariq,22,SE,68,66,70,69,83
S013,Danish Aziz,20,DS,92,90,89,95,97
S014,Nida Karim,21,AI,58,62,60,65,78
S015,Saad Mehmood,22,SE,75,78,76,80,89
S016,Rabia Anwar,20,DS,63,68,65,70,82
S017,Waqas Ahmed,23,AI,89,86,92,90,95
S018,Iqra Nawaz,21,SE,71,74,73,75,86
S019,Tariq Javed,22,DS,80,83,81,85,91
S020,Sana Riaz,20,AI,66,69,67,71,84
"""

# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------
st.header("1. Dataset")

uploaded_file = st.file_uploader("Upload student_performance.csv (optional)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("Using your uploaded CSV.")
elif os.path.exists("student_performance.csv"):
    df = pd.read_csv("student_performance.csv")
    st.info("Using local student_performance.csv found next to app.py.")
else:
    df = pd.read_csv(io.StringIO(SAMPLE_CSV))
    st.info("No file uploaded or found locally — using the built-in sample dataset "
            "so the app has something to run on. Upload your own CSV above to use real data.")

st.dataframe(df.head())
st.write(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")

# ---------------------------------------------------------
# 2. TARGET COLUMN
# ---------------------------------------------------------
st.header("2. Preprocessing")

df["Average_score"] = df[["Python", "Mathematics", "Statistics", "Machine_Learning"]].mean(axis=1)
st.write("Created `Average_score` = mean of Python, Mathematics, Statistics, Machine_Learning")

# ---------------------------------------------------------
# 3. ENCODE CATEGORICAL COLUMN
# ---------------------------------------------------------
encoder = OneHotEncoder(drop="first", sparse_output=False)
encoded_array = encoder.fit_transform(df[["Program"]])
encoded_df = pd.DataFrame(
    encoded_array,
    columns=encoder.get_feature_names_out(["Program"]),
    index=df.index,
)

col1, col2 = st.columns(2)
with col1:
    st.write("Before encoding (`Program`):")
    st.dataframe(df[["Program"]].head())
with col2:
    st.write("After One-Hot Encoding:")
    st.dataframe(encoded_df.head())

# ---------------------------------------------------------
# 4. FEATURES / TARGET
# ---------------------------------------------------------
X = pd.concat([df[["Age", "Attendance"]], encoded_df], axis=1)
y = df["Average_score"]

st.write("Feature columns (X):", list(X.columns))
st.write("Target column (y): `Average_score`")

# ---------------------------------------------------------
# 5. TRAIN-TEST SPLIT (user-adjustable)
# ---------------------------------------------------------
st.header("3. Train-Test Split & Scaling")

test_size = st.slider("Test set size", min_value=0.1, max_value=0.4, value=0.2, step=0.05)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=test_size, random_state=42
)

st.write(f"Train rows: {X_train.shape[0]}  |  Test rows: {X_test.shape[0]}")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ---------------------------------------------------------
# 6. TRAIN MODEL
# ---------------------------------------------------------
st.header("4. Model Training & Evaluation")

model = LinearRegression()
model.fit(X_train_scaled, y_train)
y_pred = model.predict(X_test_scaled)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

m1, m2, m3 = st.columns(3)
m1.metric("MAE", f"{mae:.2f}")
m2.metric("MSE", f"{mse:.2f}")
m3.metric("R² Score", f"{r2:.2f}")

if X_test.shape[0] < 6:
    st.warning("Test set is very small, so R² can look unstable or even negative. "
               "This is a dataset-size limitation, not a modeling error.")

# ---------------------------------------------------------
# 7. ACTUAL VS PREDICTED TABLE
# ---------------------------------------------------------
st.subheader("Actual vs Predicted")
comparison = pd.DataFrame({
    "Actual": y_test.values,
    "Predicted": y_pred,
    "Difference": y_test.values - y_pred,
})
st.dataframe(comparison.style.format("{:.2f}"))

# ---------------------------------------------------------
# 8. SCATTER PLOT
# ---------------------------------------------------------
st.subheader("Actual vs Predicted — Scatter Plot")

fig, ax = plt.subplots()
ax.scatter(y_test, y_pred, color="steelblue", label="Predictions")
ax.plot(
    [y_test.min(), y_test.max()],
    [y_test.min(), y_test.max()],
    color="red", linestyle="--", label="Perfect Prediction",
)
ax.set_xlabel("Actual Average Score")
ax.set_ylabel("Predicted Average Score")
ax.set_title("Actual vs Predicted Average Score")
ax.legend()
st.pyplot(fig)

# ---------------------------------------------------------
# 9. LIVE PREDICTION (bonus)
# ---------------------------------------------------------
st.header("5. Try a Prediction")
st.caption("Enter a new student's info to predict their Average_score.")

programs = df["Program"].unique().tolist()

c1, c2, c3 = st.columns(3)
age_input = c1.number_input("Age", min_value=15, max_value=40, value=20)
attendance_input = c2.number_input("Attendance (%)", min_value=0, max_value=100, value=90)
program_input = c3.selectbox("Program", programs)

if st.button("Predict Average Score"):
    new_row = pd.DataFrame({"Age": [age_input], "Attendance": [attendance_input], "Program": [program_input]})
    new_encoded = pd.DataFrame(
        encoder.transform(new_row[["Program"]]),
        columns=encoder.get_feature_names_out(["Program"]),
    )
    new_X = pd.concat([new_row[["Age", "Attendance"]], new_encoded], axis=1)
    new_X = new_X.reindex(columns=X.columns, fill_value=0)
    new_X_scaled = scaler.transform(new_X)
    prediction = model.predict(new_X_scaled)[0]
    st.success(f"Predicted Average Score: {prediction:.2f}")