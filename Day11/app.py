import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import time

st.set_page_config(page_title="Cluster & PCA Explorer", page_icon="✨", layout="wide")

# ---------------------------------------------------------
# Custom styling — mix of colors, soft animated gradient header
# ---------------------------------------------------------
st.markdown("""
<style>
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.hero {
    background: linear-gradient(270deg, #7F77DD, #1D9E75, #D85A30, #378ADD);
    background-size: 800% 800%;
    animation: gradientShift 12s ease infinite;
    padding: 2rem 2rem;
    border-radius: 16px;
    color: white;
    margin-bottom: 1.5rem;
}
.hero h1 {
    color: white;
    margin-bottom: 0.25rem;
}
.hero p {
    color: rgba(255,255,255,0.9);
    font-size: 15px;
    margin: 0;
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
.metric-card {
    animation: fadeInUp 0.6s ease;
    background: var(--surface-1, #f5f5f4);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.metric-card h2 {
    margin: 0;
    font-size: 26px;
}
.metric-card p {
    margin: 0;
    font-size: 13px;
    opacity: 0.7;
}
.stButton>button {
    transition: transform 0.15s ease;
}
.stButton>button:hover {
    transform: scale(1.03);
}
</style>
<div class="hero">
    <h1>✨ Cluster & PCA Explorer</h1>
    <p>Upload any numeric dataset — discover natural groupings with K-Means and visualize them in 3D after PCA compression.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar — data source & controls
# ---------------------------------------------------------
st.sidebar.header("1. Data")
source = st.sidebar.radio("Choose a data source", ["Use Iris sample dataset", "Upload my own CSV"])

if source == "Upload my own CSV":
    uploaded = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded is not None:
        df_raw = pd.read_csv(uploaded)
    else:
        st.info("Upload a CSV to get started, or switch to the Iris sample dataset in the sidebar.")
        st.stop()
else:
    iris = load_iris()
    df_raw = pd.DataFrame(iris.data, columns=iris.feature_names)
    df_raw["true_species"] = [iris.target_names[i] for i in iris.target]

st.sidebar.header("2. Feature selection")
numeric_cols = df_raw.select_dtypes(include=np.number).columns.tolist()

if len(numeric_cols) < 2:
    st.error("Your dataset needs at least 2 numeric columns to run clustering and PCA.")
    st.stop()

selected_cols = st.sidebar.multiselect(
    "Numeric columns to use",
    numeric_cols,
    default=numeric_cols
)

if len(selected_cols) < 2:
    st.warning("Select at least 2 numeric columns to continue.")
    st.stop()

st.sidebar.header("3. Clustering")
max_k_test = st.sidebar.slider("Max K to test (elbow method)", 2, 10, 7)
chosen_k = st.sidebar.slider("Number of clusters (K) to use", 2, max_k_test, 3)

st.sidebar.header("4. Style")
color_theme = st.sidebar.selectbox(
    "Color palette",
    ["Vivid mix", "Sunset", "Ocean", "Forest"]
)

palettes = {
    "Vivid mix": ["#7F77DD", "#1D9E75", "#D85A30", "#378ADD", "#D4537E", "#EF9F27"],
    "Sunset": ["#D85A30", "#EF9F27", "#D4537E", "#F0997B", "#993C1D"],
    "Ocean": ["#378ADD", "#1D9E75", "#185FA5", "#5DCAA5", "#042C53"],
    "Forest": ["#1D9E75", "#639922", "#3B6D11", "#97C459", "#27500A"],
}
palette = palettes[color_theme]

# ---------------------------------------------------------
# Data preview
# ---------------------------------------------------------
st.subheader("Data preview")
st.dataframe(df_raw.head(), use_container_width=True)

X = df_raw[selected_cols].dropna().values
n_samples, n_features_before = X.shape

# ---------------------------------------------------------
# Standardize + PCA
# ---------------------------------------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

n_components = 3 if len(selected_cols) >= 3 else 2
pca = PCA(n_components=n_components)
X_pca = pca.fit_transform(X_scaled)
n_features_after = X_pca.shape[1]

# ---------------------------------------------------------
# Dimensions before / after — animated metric cards
# ---------------------------------------------------------
st.subheader("Dimensions before and after PCA")

placeholder = st.empty()
with placeholder.container():
    c1, c2, c3 = st.columns(3)
    for col, label, value in zip(
        [c1, c2, c3],
        ["Rows (samples)", "Features before PCA", "Features after PCA"],
        [n_samples, n_features_before, n_features_after]
    ):
        col.markdown(
            f'<div class="metric-card"><p>{label}</p><h2>0</h2></div>',
            unsafe_allow_html=True
        )

# simple count-up animation
steps = 12
for i in range(1, steps + 1):
    with placeholder.container():
        c1, c2, c3 = st.columns(3)
        vals = [n_samples, n_features_before, n_features_after]
        labels = ["Rows (samples)", "Features before PCA", "Features after PCA"]
        for col, label, target in zip([c1, c2, c3], labels, vals):
            current = int(target * i / steps)
            col.markdown(
                f'<div class="metric-card"><p>{label}</p><h2>{current}</h2></div>',
                unsafe_allow_html=True
            )
    time.sleep(0.02)

variance_ratio = pca.explained_variance_ratio_
st.caption(
    f"PCA retained **{sum(variance_ratio)*100:.1f}%** of the original variance "
    f"across {n_features_after} component(s): "
    + ", ".join([f"PC{i+1} = {v*100:.1f}%" for i, v in enumerate(variance_ratio)])
)

# ---------------------------------------------------------
# Elbow method
# ---------------------------------------------------------
st.subheader("Elbow method — choosing K")

inertias = []
for k in range(1, max_k_test + 1):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

fig_elbow = go.Figure()
fig_elbow.add_trace(go.Scatter(
    x=list(range(1, max_k_test + 1)),
    y=inertias,
    mode="lines+markers",
    line=dict(color=palette[0], width=3),
    marker=dict(size=9, color=palette[1]),
))
fig_elbow.add_vline(x=chosen_k, line_dash="dash", line_color=palette[2],
                     annotation_text=f"Chosen K = {chosen_k}")
fig_elbow.update_layout(
    xaxis_title="K",
    yaxis_title="Inertia",
    height=380,
    margin=dict(t=20, b=20),
    transition=dict(duration=500, easing="cubic-in-out"),
)
st.plotly_chart(fig_elbow, use_container_width=True)

# ---------------------------------------------------------
# Final K-Means fit
# ---------------------------------------------------------
kmeans = KMeans(n_clusters=chosen_k, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)
df_raw_used = df_raw.loc[df_raw[selected_cols].dropna().index].copy()
df_raw_used["cluster"] = clusters.astype(str)

# ---------------------------------------------------------
# 3D cluster visualization
# ---------------------------------------------------------
st.subheader("3D cluster visualization (after PCA)")

pca_cols = [f"PC{i+1}" for i in range(n_features_after)]
df_pca = pd.DataFrame(X_pca, columns=pca_cols)
df_pca["cluster"] = clusters.astype(str)

if n_features_after >= 3:
    fig_3d = px.scatter_3d(
        df_pca, x="PC1", y="PC2", z="PC3",
        color="cluster",
        color_discrete_sequence=palette,
        opacity=0.85,
    )
else:
    fig_3d = px.scatter_3d(
        df_pca, x="PC1", y="PC2", z=[0] * len(df_pca),
        color="cluster",
        color_discrete_sequence=palette,
        opacity=0.85,
    )
    fig_3d.update_layout(scene=dict(zaxis_title=""))

fig_3d.update_traces(marker=dict(size=6, line=dict(width=0.5, color="white")))
fig_3d.update_layout(
    height=600,
    margin=dict(t=10, b=10, l=0, r=0),
    scene_camera=dict(eye=dict(x=1.4, y=1.4, z=1.1)),
    transition=dict(duration=600, easing="cubic-in-out"),
)

spin = st.checkbox("Auto-rotate the 3D plot", value=False)
st.plotly_chart(fig_3d, use_container_width=True)

if spin:
    frames = []
    for angle in range(0, 360, 6):
        rad = np.radians(angle)
        frames.append(dict(
            layout=dict(scene_camera=dict(eye=dict(x=1.6*np.cos(rad), y=1.6*np.sin(rad), z=1.1)))
        ))
    fig_spin = go.Figure(fig_3d)
    fig_spin.frames = [go.Frame(layout=f["layout"]) for f in frames]
    fig_spin.update_layout(
        updatemenus=[dict(type="buttons", showactive=False,
                           buttons=[dict(label="Play", method="animate",
                                         args=[None, dict(frame=dict(duration=60, redraw=True),
                                                           fromcurrent=True, transition=dict(duration=0))])])]
    )
    st.plotly_chart(fig_spin, use_container_width=True, key="spin_chart")

# ---------------------------------------------------------
# 2D comparison views
# ---------------------------------------------------------
st.subheader("2D comparison — original features vs PCA")

col1, col2 = st.columns(2)

with col1:
    x_feat = selected_cols[0]
    y_feat = selected_cols[1] if len(selected_cols) > 1 else selected_cols[0]
    fig_orig = px.scatter(
        df_raw_used, x=x_feat, y=y_feat, color="cluster",
        color_discrete_sequence=palette,
        title="Original features colored by cluster",
        opacity=0.85,
    )
    fig_orig.update_traces(marker=dict(size=9, line=dict(width=0.5, color="white")))
    fig_orig.update_layout(height=420, transition=dict(duration=500))
    st.plotly_chart(fig_orig, use_container_width=True)

with col2:
    fig_pca2d = px.scatter(
        df_pca, x="PC1", y="PC2", color="cluster",
        color_discrete_sequence=palette,
        title="PCA-transformed data colored by cluster",
        opacity=0.85,
    )
    fig_pca2d.update_traces(marker=dict(size=9, line=dict(width=0.5, color="white")))
    fig_pca2d.update_layout(height=420, transition=dict(duration=500))
    st.plotly_chart(fig_pca2d, use_container_width=True)

# ---------------------------------------------------------
# Cluster counts + download
# ---------------------------------------------------------
st.subheader("Cluster summary")
counts = df_raw_used["cluster"].value_counts().sort_index()
fig_bar = px.bar(
    x=counts.index, y=counts.values,
    color=counts.index, color_discrete_sequence=palette,
    labels={"x": "Cluster", "y": "Number of points"},
)
fig_bar.update_layout(height=320, showlegend=False, transition=dict(duration=400))
st.plotly_chart(fig_bar, use_container_width=True)

st.download_button(
    "Download clustered data as CSV",
    df_raw_used.to_csv(index=False).encode("utf-8"),
    file_name="clustered_data.csv",
    mime="text/csv",
)

st.caption(
    "Built with K-Means clustering + PCA. Data is standardized before both steps "
    "so features with larger numeric ranges don't dominate the result."
)