"""
app.py - Streamlit UI for the Smart Vehicle Counter (Day-39)

Features added on top of the Day-31 script:
  - Confidence + IoU threshold sliders
  - Interactive ROI (counting line) selection with a live preview
  - Tracker choice (ByteTrack vs BoT-SORT) for consistent IDs across crossings
  - Progress bar during processing
  - CSV crossing report + download
  - Support for both images and videos
  - Download buttons for processed video / image / CSV
  - Cleaner visualization (per-class colors, motion trails, stats panel)
  - Error handling around every I/O and model step
"""

import os
import tempfile

import cv2
import pandas as pd
import streamlit as st

from vehicle_counter import (
    VehicleCounter,
    VEHICLE_CLASSES,
    DEFAULT_TRACKERS,
    reencode_h264,
    write_csv,
)

st.set_page_config(page_title="Smart Vehicle Counter", page_icon="🚗", layout="wide")

st.title("🚗 Smart Vehicle Counter")
st.caption("YOLOv8 detection + tracking, counting vehicles that cross a line you draw.")

# ---------------- Sidebar: model settings ----------------
with st.sidebar:
    st.header("Detection settings")
    conf = st.slider(
        "Confidence threshold", 0.05, 0.95, 0.35, 0.05,
        help="Lower catches more vehicles but risks false positives; higher is stricter.",
    )
    iou = st.slider(
        "IoU threshold", 0.05, 0.95, 0.50, 0.05,
        help="Controls how overlapping boxes get merged during detection.",
    )
    tracker_label = st.selectbox(
        "Tracker", list(DEFAULT_TRACKERS.keys()), index=1,
        help="BoT-SORT (stable IDs) survives brief occlusion better, e.g. two vehicles crossing paths.",
    )
    trail_len = st.slider("Motion trail length (frames)", 0, 40, 15)

st.divider()

mode = st.radio("Input type", ["Video", "Image"], horizontal=True)
uploaded = st.file_uploader(
    "Upload a file",
    type=["mp4", "mov", "avi", "mkv"] if mode == "Video" else ["jpg", "jpeg", "png"],
)

if uploaded is None:
    st.info("Upload a video or image to get started.")
    st.stop()

# Persist the upload to disk so OpenCV can read it
suffix = os.path.splitext(uploaded.name)[1]
tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
tmp_in.write(uploaded.read())
tmp_in.close()
input_path = tmp_in.name

# ==================== VIDEO MODE ====================
if mode == "Video":
    cap = cv2.VideoCapture(input_path)
    ok, first_frame = cap.read()
    cap.release()

    if not ok or first_frame is None:
        st.error("Couldn't read that video - it may be corrupt or an unsupported codec.")
        st.stop()

    h, w = first_frame.shape[:2]

    st.subheader("1. Set the counting line (ROI)")
    st.caption("Vehicles are counted the moment their center crosses this line.")
    col1, col2 = st.columns(2)
    with col1:
        x1_pct = st.slider("Point A - x (%)", 0, 100, 5, key="x1")
        y1_pct = st.slider("Point A - y (%)", 0, 100, 60, key="y1")
    with col2:
        x2_pct = st.slider("Point B - x (%)", 0, 100, 95, key="x2")
        y2_pct = st.slider("Point B - y (%)", 0, 100, 60, key="y2")

    line = (
        int(w * x1_pct / 100), int(h * y1_pct / 100),
        int(w * x2_pct / 100), int(h * y2_pct / 100),
    )

    preview = first_frame.copy()
    cv2.line(preview, line[:2], line[2:], (0, 230, 255), 3)
    st.image(
        cv2.cvtColor(preview, cv2.COLOR_BGR2RGB),
        caption="Preview - drag the sliders until the line sits where you want it",
        use_container_width=True,
    )

    st.subheader("2. Process")
    if st.button("Process video", type="primary"):
        progress = st.progress(0.0, text="Loading model...")
        raw_out = input_path + "_raw.mp4"
        final_out = input_path + "_final.mp4"

        try:
            counter = VehicleCounter(
                conf=conf, iou=iou,
                tracker=DEFAULT_TRACKERS[tracker_label],
                trail_len=trail_len,
            )
            counts, log = counter.process_video(
                input_path, raw_out, line=line,
                progress_cb=lambda p: progress.progress(p, text=f"Processing frames... {p:.0%}"),
            )
            progress.progress(1.0, text="Re-encoding for browser playback...")
            reencode_h264(raw_out, final_out)
        except Exception as e:
            progress.empty()
            st.error(f"Processing failed: {e}")
            st.stop()

        progress.empty()
        st.success("Done!")

        total = sum(counts.values())
        stat_cols = st.columns(len(VEHICLE_CLASSES) + 1)
        stat_cols[0].metric("Total", total)
        for c, name in zip(stat_cols[1:], VEHICLE_CLASSES.values()):
            c.metric(name.capitalize(), counts.get(name, 0))

        st.video(final_out)

        dl_col1, dl_col2 = st.columns(2)
        with open(final_out, "rb") as f:
            dl_col1.download_button(
                "⬇ Download processed video", f,
                file_name="counted_output.mp4", mime="video/mp4",
            )

        if log:
            df = pd.DataFrame(log)
            st.dataframe(df, use_container_width=True)
            dl_col2.download_button(
                "⬇ Download CSV report", df.to_csv(index=False),
                file_name="crossing_report.csv", mime="text/csv",
            )
        else:
            dl_col2.info("No crossings were logged - try a lower confidence threshold or move the line.")

# ==================== IMAGE MODE ====================
else:
    st.image(uploaded, caption="Input image", use_container_width=True)

    if st.button("Detect vehicles", type="primary"):
        out_path = input_path + "_annotated.jpg"
        try:
            counter = VehicleCounter(conf=conf, iou=iou)
            counts = counter.process_image(input_path, out_path)
        except Exception as e:
            st.error(f"Detection failed: {e}")
            st.stop()

        st.success("Done!")
        st.image(out_path, caption="Detections", use_container_width=True)

        total = sum(counts.values())
        stat_cols = st.columns(len(VEHICLE_CLASSES) + 1)
        stat_cols[0].metric("Total", total)
        for c, name in zip(stat_cols[1:], VEHICLE_CLASSES.values()):
            c.metric(name.capitalize(), counts.get(name, 0))

        with open(out_path, "rb") as f:
            st.download_button(
                "⬇ Download annotated image", f,
                file_name="detected.jpg", mime="image/jpeg",
            )
