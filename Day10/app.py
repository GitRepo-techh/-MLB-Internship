import io

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler

st.set_page_config(
    page_title="Breast Cancer Prediction System",
    layout="wide",
)

# ----------------------------------------------------------------------
# Cached helpers
# ----------------------------------------------------------------------


@st.cache_data
def get_data():
    data = load_breast_cancer()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df["target"] = data.target
    return data, df


@st.cache_data
def split_and_scale(_X, _y, test_size, random_state):
    X_train, X_test, y_train, y_test = train_test_split(
        _X, _y, test_size=test_size, random_state=random_state, stratify=_y
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, y_train, y_test


@st.cache_resource
def train_baseline(X_train_scaled, y_train, random_state):
    model = LogisticRegression(max_iter=5000, random_state=random_state)
    model.fit(X_train_scaled, y_train)
    return model


@st.cache_resource
def run_grid_search(X_train_scaled, y_train, cv, scoring):
    param_grid = {
        "C": [0.01, 0.1, 1, 10, 100],
        "penalty": ["l1", "l2"],
        "solver": ["liblinear", "saga"],
    }
    base_model = LogisticRegression(max_iter=5000, random_state=42)
    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        cv=cv,
        scoring=scoring,
        n_jobs=-1,
    )
    grid_search.fit(X_train_scaled, y_train)
    return grid_search


def compute_metrics(model, X_test_scaled, y_test):
    y_pred = model.predict(X_test_scaled)
    metrics = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1-Score": f1_score(y_test, y_pred),
    }
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=target_names_global)
    return y_pred, metrics, cm, report


def plot_cm(cm, target_names, title, cmap):
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap=cmap,
        xticklabels=target_names,
        yticklabels=target_names,
        ax=ax,
    )
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("Actual Label")
    ax.set_title(title)
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------
# Sidebar controls
# ----------------------------------------------------------------------

st.title("🩺 Breast Cancer Prediction System")
st.caption(
    "Model Evaluation & Hyperparameter Tuning with Logistic Regression "
    "on the Breast Cancer Wisconsin dataset."
)

with st.sidebar:
    st.header("⚙️ Settings")
    test_size = st.slider("Test size", 0.1, 0.4, 0.2, 0.05)
    random_state = st.number_input("Random state", value=69, step=1)
    cv_folds = st.slider("CV folds (GridSearchCV)", 3, 10, 5)
    scoring = st.selectbox(
        "Scoring metric for tuning",
        ["recall", "accuracy", "precision", "f1"],
        index=0,
    )
    run_button = st.button("🚀 Run Pipeline", type="primary", use_container_width=True)

data, df = get_data()
target_names_global = data.target_names

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Data Exploration", "📈 Baseline Model", "🔧 Hyperparameter Tuning", "⚖️ Comparison"]
)

# ----------------------------------------------------------------------
# Tab 1: Data Exploration
# ----------------------------------------------------------------------
with tab1:
    st.subheader("Dataset Preview")
    st.dataframe(df.head(), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("df.info()")
        buffer = io.StringIO()
        df.info(buf=buffer)
        st.text(buffer.getvalue())
    with col2:
        st.subheader("df.describe()")
        st.dataframe(df.describe(), use_container_width=True)

    st.subheader("Target Class Distribution")
    counts = df["target"].value_counts().sort_index()
    counts.index = [target_names_global[i] for i in counts.index]
    c1, c2 = st.columns([1, 2])
    with c1:
        st.dataframe(counts.rename("count"))
    with c2:
        fig, ax = plt.subplots(figsize=(5, 3.5))
        sns.barplot(x=counts.index, y=counts.values, ax=ax, palette="viridis")
        ax.set_ylabel("Count")
        ax.set_xlabel("Class")
        ax.set_title("Target Class Distribution")
        fig.tight_layout()
        st.pyplot(fig)

# ----------------------------------------------------------------------
# Run pipeline (shared across tabs, stored in session_state)
# ----------------------------------------------------------------------
if run_button:
    X, y = data.data, data.target
    X_train_scaled, X_test_scaled, y_train, y_test = split_and_scale(
        X, y, test_size, int(random_state)
    )

    baseline_model = train_baseline(X_train_scaled, y_train, int(random_state))
    _, baseline_metrics, baseline_cm, baseline_report = compute_metrics(
        baseline_model, X_test_scaled, y_test
    )

    grid_search = run_grid_search(X_train_scaled, y_train, cv_folds, scoring)
    tuned_model = grid_search.best_estimator_
    _, tuned_metrics, tuned_cm, tuned_report = compute_metrics(
        tuned_model, X_test_scaled, y_test
    )

    st.session_state["results"] = {
        "baseline_metrics": baseline_metrics,
        "baseline_cm": baseline_cm,
        "baseline_report": baseline_report,
        "tuned_metrics": tuned_metrics,
        "tuned_cm": tuned_cm,
        "tuned_report": tuned_report,
        "best_params": grid_search.best_params_,
        "best_cv_score": grid_search.best_score_,
        "scoring": scoring,
    }

results = st.session_state.get("results")

# ----------------------------------------------------------------------
# Tab 2: Baseline Model
# ----------------------------------------------------------------------
with tab2:
    if not results:
        st.info("👈 Click **Run Pipeline** in the sidebar to train the models.")
    else:
        st.subheader("Baseline Logistic Regression")
        m = results["baseline_metrics"]
        cols = st.columns(4)
        for col, (name, value) in zip(cols, m.items()):
            col.metric(name, f"{value:.4f}")

        c1, c2 = st.columns([1, 1])
        with c1:
            fig = plot_cm(
                results["baseline_cm"],
                target_names_global,
                "Baseline - Confusion Matrix",
                "Blues",
            )
            st.pyplot(fig)
        with c2:
            st.text("Classification Report")
            st.text(results["baseline_report"])

# ----------------------------------------------------------------------
# Tab 3: Hyperparameter Tuning
# ----------------------------------------------------------------------
with tab3:
    if not results:
        st.info("👈 Click **Run Pipeline** in the sidebar to run GridSearchCV.")
    else:
        st.subheader("GridSearchCV Results")
        st.write(f"**Scoring used:** `{results['scoring']}`")
        st.write("**Best Parameters:**", results["best_params"])
        st.write(f"**Best CV Score:** {results['best_cv_score']:.4f}")

        st.subheader("Tuned Logistic Regression")
        m = results["tuned_metrics"]
        cols = st.columns(4)
        for col, (name, value) in zip(cols, m.items()):
            col.metric(name, f"{value:.4f}")

        c1, c2 = st.columns([1, 1])
        with c1:
            fig = plot_cm(
                results["tuned_cm"],
                target_names_global,
                "Tuned - Confusion Matrix",
                "Greens",
            )
            st.pyplot(fig)
        with c2:
            st.text("Classification Report")
            st.text(results["tuned_report"])

# ----------------------------------------------------------------------
# Tab 4: Comparison
# ----------------------------------------------------------------------
with tab4:
    if not results:
        st.info("👈 Click **Run Pipeline** in the sidebar to compare models.")
    else:
        st.subheader("Baseline vs Tuned")
        comp_df = pd.DataFrame(
            {
                "Baseline": results["baseline_metrics"],
                "Tuned": results["tuned_metrics"],
            }
        )
        comp_df["Improvement"] = comp_df["Tuned"] - comp_df["Baseline"]
        st.dataframe(comp_df.style.format("{:.4f}"), use_container_width=True)

        fig, ax = plt.subplots(figsize=(7, 4))
        comp_df[["Baseline", "Tuned"]].plot(kind="bar", ax=ax, color=["#4C72B0", "#55A868"])
        ax.set_ylabel("Score")
        ax.set_title("Baseline vs Tuned Metrics")
        ax.set_ylim(0, 1.05)
        plt.xticks(rotation=0)
        fig.tight_layout()
        st.pyplot(fig)

        improved = (comp_df["Improvement"] > 0).sum()
        st.success(
            f"✅ {improved} out of 4 metrics improved after hyperparameter tuning."
            if improved > 0
            else "ℹ️ Tuning did not improve metrics on this split — try a different scoring metric or CV folds."
        )