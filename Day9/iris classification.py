# 1. Load and explore the dataset
# 2. Train a Logistic Regression model
# 3. Predict flower species
# 4. Display model evaluation metrics
# 5. Show the Confusion Matrix
# 6. Print sample predictions with actual values

#Bonus:
# - Train a Decision Tree model
# - Compare its performance with Logistic Regression


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


def load_and_explore():
    """Step 1: Load and explore the Iris dataset."""
    iris = load_iris()
    X, y = iris.data, iris.target
    df = pd.DataFrame(X, columns=iris.feature_names)
    df["species"] = pd.Categorical.from_codes(y, iris.target_names)

    print("=" * 60)
    print("IRIS FLOWER CLASSIFICATION SYSTEM")
    print("=" * 60)
    print(f"\nDataset shape        : {X.shape}")
    print(f"Features             : {iris.feature_names}")
    print(f"Target species       : {list(iris.target_names)}")
    print(f"Class balance        :\n{df['species'].value_counts()}")

    return X, y, iris.feature_names, iris.target_names, df


def train_model(model, X_train, y_train, name):
    """Fit any sklearn classifier and label it for reporting."""
    model.fit(X_train, y_train)
    print(f"\n[{name}] training complete.")
    return model


def evaluate_model(model, X_test, y_test, target_names, name):
    """Step 4/5: Compute metrics and confusion matrix for a trained model."""
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="macro")
    rec = recall_score(y_test, y_pred, average="macro")
    f1 = f1_score(y_test, y_pred, average="macro")
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n--- {name}: Evaluation Metrics ---")
    print(f"Accuracy  : {acc:.4f}")
    print(f"Precision : {prec:.4f}")
    print(f"Recall    : {rec:.4f}")
    print(f"F1-Score  : {f1:.4f}")
    print(f"\nConfusion Matrix:\n{cm}")

    plt.figure(figsize=(5, 4))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=target_names, yticklabels=target_names,
    )
    plt.title(f"Confusion Matrix - {name}")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    filename = f"confusion_matrix_{name.lower().replace(' ', '_')}.png"
    plt.savefig(filename, dpi=120)
    plt.close()
    print(f"Saved -> {filename}")

    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}, y_pred


def print_sample_predictions(X_test, y_test, y_pred, target_names, n=10):
    """Step 6: Print a handful of sample predictions vs actual values."""
    print("\n--- Sample Predictions (Predicted vs Actual) ---")
    n = min(n, len(y_test))
    for i in range(n):
        pred_name = target_names[y_pred[i]]
        actual_name = target_names[y_test[i]]
        result = "CORRECT" if y_pred[i] == y_test[i] else "WRONG"
        print(f"Sample {i+1:2d}: Predicted = {pred_name:<12} | Actual = {actual_name:<12} | {result}")


def main():
    # 1. Load and explore
    X, y, feature_names, target_names, df = load_and_explore()

    # 2. Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. Train Logistic Regression (primary model)
    log_reg = LogisticRegression(max_iter=200)
    log_reg = train_model(log_reg, X_train, y_train, "Logistic Regression")

    # 4 & 5. Evaluate + confusion matrix
    lr_metrics, lr_preds = evaluate_model(
        log_reg, X_test, y_test, target_names, "Logistic Regression"
    )

    # 6. Sample predictions
    print_sample_predictions(X_test, y_test, lr_preds, target_names)

    # ---------------- BONUS: Decision Tree comparison ----------------
    print("\n" + "=" * 60)
    print("BONUS: DECISION TREE COMPARISON")
    print("=" * 60)

    dtree = DecisionTreeClassifier(random_state=42, max_depth=3)
    dtree = train_model(dtree, X_train, y_train, "Decision Tree")
    dt_metrics, dt_preds = evaluate_model(
        dtree, X_test, y_test, target_names, "Decision Tree"
    )
    print_sample_predictions(X_test, y_test, dt_preds, target_names)

    # ---------------- Side-by-side comparison table ----------------
    print("\n" + "=" * 60)
    print("MODEL COMPARISON: LOGISTIC REGRESSION vs DECISION TREE")
    print("=" * 60)
    comparison = pd.DataFrame(
        {"Logistic Regression": lr_metrics, "Decision Tree": dt_metrics}
    ).T
    print(comparison.round(4))

    better = "Logistic Regression" if lr_metrics["f1"] >= dt_metrics["f1"] else "Decision Tree"
    print(f"\nBased on F1-Score, '{better}' performed better on this test split.")


    comparison.to_csv("model_comparison.csv")


if __name__ == "__main__":
    main()