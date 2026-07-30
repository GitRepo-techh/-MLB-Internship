import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score,f1_score, confusion_matrix, classification_report


def load_and_split(test_size=0.2, random_state=69):
    data = load_breast_cancer()
    X, y = data.data, data.target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return data, X_train, X_test, y_train, y_test


def scale_features(X_train, X_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return scaler, X_train_scaled, X_test_scaled


def tune_model(X_train_scaled, y_train):
    param_grid = {
        "C": [0.01, 0.1, 1, 10, 100],
        "penalty": ["l1", "l2"],
        "solver": ["liblinear", "saga"],
    }
    base_model = LogisticRegression(max_iter=5000, random_state=42)
    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        cv=5,
        scoring="recall",
        n_jobs=-1,
    )
    grid_search.fit(X_train_scaled, y_train)
    return grid_search


def evaluate(model, X_test_scaled, y_test, target_names, label="Model"):
    y_pred = model.predict(X_test_scaled)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
    }
    cm = confusion_matrix(y_test, y_pred)

    print("=" * 50)
    print(f"{label.upper()} - EVALUATION")
    print("=" * 50)
    for name, value in metrics.items():
        print(f"{name.capitalize():<10}: {value:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=target_names))

    return y_pred, metrics, cm


def plot_confusion_matrix(cm, target_names, title, filename, cmap="Blues"):
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap=cmap,
        xticklabels=target_names, yticklabels=target_names
    )
    plt.xlabel("Predicted Label")
    plt.ylabel("Actual Label")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.show()
    print(f"Saved: {filename}")


def main():
    # 1. Load and split
    data, X_train, X_test, y_train, y_test = load_and_split()
    target_names = data.target_names

    # 2. Scale
    scaler, X_train_scaled, X_test_scaled = scale_features(X_train, X_test)

    # 3. Baseline model
    baseline_model = LogisticRegression(max_iter=5000, random_state=42)
    baseline_model.fit(X_train_scaled, y_train)
    _, baseline_metrics, baseline_cm = evaluate(
        baseline_model, X_test_scaled, y_test, target_names, label="Baseline"
    )
    plot_confusion_matrix(
        baseline_cm, target_names,
        "Baseline Logistic Regression - Confusion Matrix",
        "baseline_confusion_matrix.png", cmap="Blues"
    )

    # 4. Hyperparameter tuning
    grid_search = tune_model(X_train_scaled, y_train)
    print("\nBest Parameters:", grid_search.best_params_)
    print("Best CV Recall Score:", grid_search.best_score_)

    tuned_model = grid_search.best_estimator_
    _, tuned_metrics, tuned_cm = evaluate(
        tuned_model, X_test_scaled, y_test, target_names, label="Tuned"
    )
    plot_confusion_matrix(
        tuned_cm, target_names,
        "Tuned Logistic Regression - Confusion Matrix",
        "tuned_confusion_matrix.png", cmap="Greens"
    )

    # 5. Comparison summary
    print("\n" + "=" * 50)
    print("COMPARISON: BASELINE vs TUNED")
    print("=" * 50)
    print(f"{'Metric':<12}{'Baseline':<12}{'Tuned':<12}")
    for key in baseline_metrics:
        print(f"{key.capitalize():<12}{baseline_metrics[key]:<12.4f}{tuned_metrics[key]:<12.4f}")


if __name__ == "__main__":
    main()