import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


iris = load_iris()
x = iris.data                
y = iris.target               
feature_names = iris.feature_names
target_names = iris.target_names

print("=" * 60)
print("STEP 1: LOAD DATASET")
print("=" * 60)
print(f"Feature names : {feature_names}")
print(f"Target classes: {target_names}")
print(f"Data shape    : {x.shape}")


df = pd.DataFrame(x, columns=feature_names)
df["species"] = pd.Categorical.from_codes(y, target_names)

print(df.head())


print(df.describe())


print(df["species"].value_counts())


print(df.isnull().sum())


sns.pairplot(df, hue="species", diag_kind="hist")
plt.suptitle("Iris Feature Relationships by Species", y=1.02)
plt.savefig("iris_pairplot.png", dpi=120, bbox_inches="tight")
plt.close()



X_train, X_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42, stratify=y
)

print("\n" + "=" * 60)
print("STEP 3: TRAIN/TEST SPLIT")

print(f"Training samples: {X_train.shape[0]}")
print(f"Testing samples : {X_test.shape[0]}")

model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)


print("Model trained successfully.")


y_pred = model.predict(X_test)

print(f"Predicted labels: {y_pred}")
print(f"Actual labels   : {y_test}")





accuracy = accuracy_score(y_test, y_pred)
# 'macro' averaging treats every class equally -> good for balanced multi-class problems like Iris
precision = precision_score(y_test, y_pred, average="macro")
recall = recall_score(y_test, y_pred, average="macro")
f1 = f1_score(y_test, y_pred, average="macro")

print(f"Accuracy  : {accuracy:.4f}   -> % of all predictions that were correct")
print(f"Precision : {precision:.4f}   -> of predicted positives, % that were actually correct")
print(f"Recall    : {recall:.4f}   -> of actual positives, % that were correctly found")
print(f"F1-Score  : {f1:.4f}   -> harmonic mean of precision and recall")


print(classification_report(y_test, y_pred, target_names=target_names))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix (rows = actual, columns = predicted):")
print(cm)

plt.figure(figsize=(6, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=target_names,
    yticklabels=target_names,
)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - Logistic Regression on Iris")
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=120)
plt.close()

