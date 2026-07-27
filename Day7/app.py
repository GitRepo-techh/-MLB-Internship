import streamlit as st
import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
chart_dir = os.path.join(script_dir, "Chart images")

df = pd.read_csv(os.path.join(script_dir, "cleaned_student_performance.csv"))

st.title("Student Performance Dashboard")

# --- Key Stats ---
st.header("Key Stats")
st.write("Total Students:", len(df))

subjects = ["Python", "Mathematics", "Statistics", "Machine_Learning"]
subject_avg = df[subjects].mean()
st.write("Average Score per Subject:")
st.dataframe(subject_avg)

st.write("Subject with Highest Average:", subject_avg.idxmax())

top5 = df.sort_values(by="Average_Score", ascending=False).head(5)
st.write("Top 5 Students:")
st.dataframe(top5[["Name", "Average_Score"]])

needs_improvement = df[df["Performance"] == "Needs Improvement"]
st.write("Students Needing Improvement:")
st.dataframe(needs_improvement[["Name", "Average_Score"]])

# --- Charts ---
st.header("Charts")
st.image(os.path.join(chart_dir, "bar_avg_score.png"), caption="Average Score per Student")
st.image(os.path.join(chart_dir, "hist_avg_score.png"), caption="Distribution of Average Scores")
st.image(os.path.join(chart_dir, "scatter_python_ml.png"), caption="Python vs Machine Learning")
st.image(os.path.join(chart_dir, "pie_performance.png"), caption="Performance Categories")
st.image(os.path.join(chart_dir, "box_subjects.png"), caption="Marks Across Subjects")
st.image(os.path.join(script_dir, "dashboard_subject_avg.png"), caption="Average Score per Subject")
st.image(os.path.join(script_dir, "dashboard_top5.png"), caption="Top 5 Students")