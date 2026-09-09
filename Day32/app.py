import os
import tempfile

import streamlit as st

from traffic_violation import process_video
from analytics import save_stats_json, save_events_csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_videos")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_PATH = "yolov8n.pt"

st.set_page_config(page_title="Traffic Violation Monitor", layout="wide")
st.title("🚦 AI Traffic Violation Monitoring System")
st.caption("YOLOv8 detection + ByteTrack tracking + rule-based direction & zone violations")

with st.sidebar:
    st.header("Settings")

    uploaded_file = st.file_uploader("Upload a traffic video", type=["mp4", "mov", "avi"])

    variant_label = st.selectbox(
        "Select analysis mode",
        ["Wrong-Way Detection", "Traffic Violation Analytics"],
    )
    variant = "wrong_way" if variant_label == "Wrong-Way Detection" else "dashboard"

    st.markdown("**Normal traffic direction** (for wrong-way logic)")
    direction_choice = st.selectbox(
        "Direction",
        ["Top → Bottom", "Bottom → Top", "Left → Right", "Right → Left"],
    )
    direction_map = {
        "Top → Bottom": (0, 1),
        "Bottom → Top": (0, -1),
        "Left → Right": (1, 0),
        "Right → Left": (-1, 0),
    }
    normal_direction = direction_map[direction_choice]

    confidence = st.slider("Detection confidence threshold", 0.1, 0.9, 0.3, 0.05)

    run_button = st.button("▶ Run Analysis", type="primary")

if run_button:
    if uploaded_file is None:
        st.error("Please upload a video first.")
        st.stop()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", dir=OUTPUT_DIR) as tmp_in:
        tmp_in.write(uploaded_file.read())
        input_path = tmp_in.name

    output_path = os.path.join(OUTPUT_DIR, f"processed_{variant}.mp4")

    with st.spinner("Running detection, tracking, and violation analysis..."):
        stats = process_video(
            input_path=input_path,
            output_path=output_path,
            variant=variant,
            model_path=MODEL_PATH,
            normal_direction=normal_direction,
            conf=confidence,
        )

    st.success("Analysis complete.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Processed Video")
        st.video(output_path)
        with open(output_path, "rb") as f:
            st.download_button("⬇ Download processed video", f, file_name=f"processed_{variant}.mp4")

    with col2:
        st.subheader("Violation Statistics")
        st.metric("Total Vehicles", stats["total_vehicles"])
        st.metric("Total Violations", stats["total_violations"])
        st.metric("Wrong-Way Violations", stats["wrong_way_violations"])
        st.metric("Restricted Zone Violations", stats["restricted_zone_violations"])

        st.markdown("**Vehicle Type Counts**")
        st.table(stats["vehicle_type_counts"])

        st.markdown("**Violation Events**")
        st.dataframe(stats["violation_events"])

    stats_json_path = os.path.join(OUTPUT_DIR, "stats.json")
    events_csv_path = os.path.join(OUTPUT_DIR, "events.csv")
    save_stats_json(stats, stats_json_path)
    save_events_csv(stats, events_csv_path)

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        with open(stats_json_path, "rb") as f:
            st.download_button("⬇ Download stats (JSON)", f, file_name="stats.json")
    with dcol2:
        with open(events_csv_path, "rb") as f:
            st.download_button("⬇ Download violation events (CSV)", f, file_name="events.csv")

else:
    st.info("Upload a video and click **Run Analysis** in the sidebar to get started.")
    if os.path.isdir(SAMPLE_DIR) and os.listdir(SAMPLE_DIR):
        st.caption(f"Sample videos available in `sample_videos/`: {', '.join(os.listdir(SAMPLE_DIR))}")
