import streamlit as st
import pandas as pd
import numpy as np
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

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Iris Flower Classification System",
    page_icon="🌸",
    layout="wide",
)

# ----------------------------------------------------------------------
# LOAD DATA + TRAIN MODELS (cached so it only runs once)
# ----------------------------------------------------------------------
@st.cache_data
def load_data():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["species"] = pd.Categorical.from_codes(iris.target, iris.target_names)
    return df, iris.data, iris.target, iris.feature_names, iris.target_names


@st.cache_resource
def train_models(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    log_reg = LogisticRegression(max_iter=200).fit(X_train, y_train)
    dtree = DecisionTreeClassifier(max_depth=3, random_state=42).fit(X_train, y_train)

    results = {}
    for name, model in [("Logistic Regression", log_reg), ("Decision Tree", dtree)]:
        y_pred = model.predict(X_test)
        results[name] = {
            "model": model,
            "y_pred": y_pred,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average="macro"),
            "recall": recall_score(y_test, y_pred, average="macro"),
            "f1": f1_score(y_test, y_pred, average="macro"),
            "cm": confusion_matrix(y_test, y_pred),
        }

    return results, X_test, y_test, log_reg


df, X, y, feature_names, target_names = load_data()
results, X_test, y_test, primary_model = train_models(X, y)

# ----------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------
st.title("🌸 Iris Flower Classification System")
st.caption("Day 9 - MLB Internship | Logistic Regression vs Decision Tree")

tab1, tab2, tab3 = st.tabs(["📊 Dataset", "🎯 Model Evaluation", "🔮 Try a Prediction"])

# ----------------------------------------------------------------------
# TAB 1: DATASET
# ----------------------------------------------------------------------
with tab1:
    st.subheader("Dataset Overview")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(df.head(10), use_container_width=True)

    with col2:
        st.markdown("**Samples per species**")
        counts = df["species"].value_counts()
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.barplot(x=counts.index, y=counts.values, ax=ax, palette="Blues_d")
        ax.set_ylabel("Count")
        ax.set_xlabel("")
        st.pyplot(fig)

    st.markdown("---")
    st.markdown("**Statistical Summary**")
    st.dataframe(df.describe(), use_container_width=True)

    st.markdown("**Feature Relationships**")
    fig2 = sns.pairplot(df, hue="species", diag_kind="hist")
    st.pyplot(fig2)

# ----------------------------------------------------------------------
# TAB 2: MODEL EVALUATION
# ----------------------------------------------------------------------
with tab2:
    st.subheader("Model Evaluation")

    metric_cols = st.columns(2)
    for col, (name, res) in zip(metric_cols, results.items()):
        with col:
            st.markdown(f"### {name}")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Accuracy", f"{res['accuracy']:.2%}")
            m2.metric("Precision", f"{res['precision']:.2%}")
            m3.metric("Recall", f"{res['recall']:.2%}")
            m4.metric("F1-Score", f"{res['f1']:.2%}")

            fig, ax = plt.subplots(figsize=(4, 3.5))
            sns.heatmap(
                res["cm"], annot=True, fmt="d", cmap="Blues",
                xticklabels=target_names, yticklabels=target_names, ax=ax,
            )
            ax.set_xlabel("Predicted")
            ax.set_ylabel("Actual")
            ax.set_title(f"Confusion Matrix - {name}")
            st.pyplot(fig)

    st.markdown("---")
    st.markdown(
        "**Observation:** Setosa is always perfectly separated. The only "
        "confusion happens between *versicolor* and *virginica*, whose petal "
        "measurements overlap — a well-known trait of the Iris dataset."
    )

# ----------------------------------------------------------------------
# TAB 3: TRY A PREDICTION
# ----------------------------------------------------------------------
with tab3:
    st.subheader("Try a Prediction")
    st.write("Adjust the flower measurements below and see the predicted species.")

    c1, c2 = st.columns(2)
    with c1:
        sepal_length = st.slider("Sepal Length (cm)", float(df.iloc[:, 0].min()), float(df.iloc[:, 0].max()), float(df.iloc[:, 0].mean()))
        sepal_width = st.slider("Sepal Width (cm)", float(df.iloc[:, 1].min()), float(df.iloc[:, 1].max()), float(df.iloc[:, 1].mean()))
    with c2:
        petal_length = st.slider("Petal Length (cm)", float(df.iloc[:, 2].min()), float(df.iloc[:, 2].max()), float(df.iloc[:, 2].mean()))
        petal_width = st.slider("Petal Width (cm)", float(df.iloc[:, 3].min()), float(df.iloc[:, 3].max()), float(df.iloc[:, 3].mean()))

    input_data = np.array([[sepal_length, sepal_width, petal_length, petal_width]])

    if st.button("Predict Species", type="primary"):
        prediction = primary_model.predict(input_data)[0]
        probabilities = primary_model.predict_proba(input_data)[0]

        st.success(f"Predicted Species: **{target_names[prediction].capitalize()}**")

        prob_df = pd.DataFrame({
            "Species": target_names,
            "Probability": probabilities,
        }).set_index("Species")
        st.bar_chart(prob_df)

st.markdown("---")
st.caption("Built with Streamlit • scikit-learn • MLB Internship Day 9")