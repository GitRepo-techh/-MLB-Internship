import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. LOAD DATA
df = pd.read_csv("student_performance.csv")

# 2. CREATE TARGET COLUMN
# Average_score = mean of the 4 subject scores (this is what we're predicting)
df["Average_score"] = df[["Python", "Mathematics", "Statistics", "Machine_Learning"]].mean(axis=1)

# One-Hot Encoding
encoder = OneHotEncoder(drop="first", sparse_output=False)
encoded_array = encoder.fit_transform(df[["Program"]])
encoded_df = pd.DataFrame(encoded_array, columns=encoder.get_feature_names_out(["Program"]))

# 4. BUILD X (features) and y (target)

X = pd.concat([df[["Age", "Attendance"]], encoded_df], axis=1)
y = df["Average_score"]

# 5. TRAIN-TEST SPLIT (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 6. FEATURE SCALING

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 7. TRAIN THE MODEL
model = LinearRegression()
model.fit(X_train_scaled, y_train)

# 8. PREDICT
y_pred = model.predict(X_test_scaled)

# 9. EVALUATE
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MAE: {mae:.2f}")
print(f"MSE: {mse:.2f}")
print(f"R² Score: {r2:.2f}")


comparison = pd.DataFrame({"Actual": y_test.values, "Predicted": y_pred})
print(comparison)


plt.scatter(y_test, y_pred, color="blue", label="Predictions")
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color="red", label="Perfect Prediction")
plt.xlabel("Actual Average Score")
plt.ylabel("Predicted Average Score")
plt.title("Actual vs Predicted Average Score")
plt.legend()
plt.show()

