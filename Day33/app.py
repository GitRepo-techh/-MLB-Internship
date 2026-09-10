"""
Day 37 Mini Project - Smart People Counting System
Streamlit app: upload an image or video, detect + track people with
YOLOv8 + ByteTrack, and optionally run line-crossing entry/exit counting
or region-based occupancy counting. Saves the processed output.

Run:
    uv run streamlit run app.py
"""

import os
import tempfile
import subprocess
import numpy as np
import cv2
import streamlit as st
from ultralytics import YOLO
import imageio_ffmpeg

st.set_page_config(page_title="Smart People Counting System", layout="wide")

PERSON_CLASS_ID = 0  # COCO class 0 = person

# Bundled static ffmpeg binary — works the same on Windows and Streamlit
# Cloud, no system install or packages.txt entry required.
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()


@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")


def reencode_h264(raw_path: str, final_path: str) -> None:
    cmd = [FFMPEG_EXE, "-y", "-i", raw_path, "-vcodec", "libx264", "-pix_fmt", "yuv420p", final_path]
    subprocess.run(cmd, check=True, capture_output=True)
    os.remove(raw_path)


def point_in_rect(cx, cy, rect):
    x1, y1, x2, y2 = rect
    return x1 <= cx <= x2 and y1 <= cy <= y2


def process_image(model, image, conf):
    result = model.predict(image, classes=[PERSON_CLASS_ID], conf=conf, verbose=False)[0]
    frame = image.copy()
    count = 0
    if result.boxes is not None:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            c = float(box.conf[0])
            count += 1
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
            cv2.putText(frame, f"{c:.2f}", (x1, max(y1 - 8, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 2)
    cv2.putText(frame, f"People Count: {count}", (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    return frame, count


def process_video(model, input_path, conf, mode, line_y_frac=None, region_frac=None, progress_cb=None):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

    raw_path = os.path.join(tempfile.gettempdir(), "raw_output.mp4")
    final_path = os.path.join(tempfile.gettempdir(), "people_counted_output.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(raw_path, fourcc, fps, (width, height))

    line_y = int(height * line_y_frac) if line_y_frac is not None else None
    region = None
    if region_frac is not None:
        rx1, ry1, rx2, ry2 = region_frac
        region = (int(rx1 * width), int(ry1 * height), int(rx2 * width), int(ry2 * height))

    prev_centroids = {}   # track_id -> last (cx, cy), used for line-crossing direction
    entries, exits = 0, 0
    unique_ids = set()
    unique_region_ids = set()
    max_count = 0
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1

        result = model.track(frame, classes=[PERSON_CLASS_ID], conf=conf,
                              persist=True, tracker="bytetrack.yaml", verbose=False)[0]

        current_count = 0
        inside_region_now = set()

        boxes = result.boxes
        if boxes is not None and boxes.id is not None:
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            ids = boxes.id.cpu().numpy().astype(int)
            current_count = len(ids)
            max_count = max(max_count, current_count)

            for (x1, y1, x2, y2), c, tid in zip(xyxy, confs, ids):
                unique_ids.add(tid)
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
                cv2.putText(frame, f"ID {tid} {c:.2f}", (x1, max(y1 - 8, 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 0), 2)

                if mode == "Line Crossing" and line_y is not None:
                    prev = prev_centroids.get(tid)
                    if prev is not None:
                        prev_cy = prev[1]
                        if prev_cy < line_y <= cy:
                            entries += 1
                        elif prev_cy > line_y >= cy:
                            exits += 1
                    prev_centroids[tid] = (cx, cy)

                if mode == "Region Based" and region is not None:
                    if point_in_rect(cx, cy, region):
                        inside_region_now.add(tid)
                        unique_region_ids.add(tid)

        if mode == "Line Crossing" and line_y is not None:
            cv2.line(frame, (0, line_y), (width, line_y), (0, 0, 255), 2)
            cv2.putText(frame, f"Entries: {entries}  Exits: {exits}", (15, height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        if mode == "Region Based" and region is not None:
            rx1, ry1, rx2, ry2 = region
            cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), (255, 0, 0), 2)
            cv2.putText(frame, f"Inside Region: {len(inside_region_now)}", (15, height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        cv2.rectangle(frame, (0, 0), (300, 70), (0, 0, 0), -1)
        cv2.putText(frame, f"Live Count: {current_count}", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(frame, f"Max Count: {max_count}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        writer.write(frame)

        if progress_cb:
            progress_cb(min(frame_idx / total_frames, 1.0))

    cap.release()
    writer.release()
    reencode_h264(raw_path, final_path)

    return {
        "unique_people": len(unique_ids),
        "max_count": max_count,
        "entries": entries,
        "exits": exits,
        "unique_region_visitors": len(unique_region_ids),
        "output_path": final_path,
    }


# ---------------------- UI ----------------------

st.title("Smart People Counting System")
st.caption("YOLOv8 + ByteTrack | Day 37 Mini Project")

model = load_model()

with st.sidebar:
    st.header("Settings")
    conf = st.slider("Confidence threshold", 0.1, 0.9, 0.35, 0.05)
    file_type = st.radio("Input type", ["Video", "Image"])

    mode = "None"
    line_y_frac = None
    region_frac = None

    if file_type == "Video":
        mode = st.selectbox("Counting mode", ["None", "Line Crossing", "Region Based"])
        if mode == "Line Crossing":
            line_y_frac = st.slider("Line position (fraction of height)", 0.1, 0.9, 0.5, 0.05)
        elif mode == "Region Based":
            st.write("Define ROI rectangle (fractions of frame)")
            rx1 = st.slider("x1", 0.0, 1.0, 0.2, 0.05)
            ry1 = st.slider("y1", 0.0, 1.0, 0.2, 0.05)
            rx2 = st.slider("x2", 0.0, 1.0, 0.8, 0.05)
            ry2 = st.slider("y2", 0.0, 1.0, 0.8, 0.05)
            region_frac = (rx1, ry1, rx2, ry2)

uploaded = st.file_uploader(
    "Upload an image or video",
    type=["jpg", "jpeg", "png", "mp4", "mov", "avi"],
)

if uploaded is not None:
    if file_type == "Image":
        file_bytes = np.frombuffer(uploaded.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        with st.spinner("Detecting people..."):
            processed, count = process_image(model, image, conf)

        st.subheader(f"People Detected: {count}")
        st.image(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB), use_container_width=True)

        out_path = os.path.join(tempfile.gettempdir(), "counted_image.jpg")
        cv2.imwrite(out_path, processed)
        with open(out_path, "rb") as f:
            st.download_button("Download processed image", f, file_name="people_counted.jpg")

    else:
        tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp_in.write(uploaded.read())
        tmp_in.close()

        st.video(tmp_in.name)
        progress_bar = st.progress(0.0)

        with st.spinner("Processing video (detecting + tracking)..."):
            stats = process_video(
                model, tmp_in.name, conf, mode,
                line_y_frac=line_y_frac, region_frac=region_frac,
                progress_cb=progress_bar.progress,
            )

        st.success("Done!")
        col1, col2, col3 = st.columns(3)
        col1.metric("Unique people tracked", stats["unique_people"])
        col2.metric("Peak occupancy (max count)", stats["max_count"])

        if mode == "Line Crossing":
            col3.metric("Entries / Exits", f"{stats['entries']} / {stats['exits']}")
        elif mode == "Region Based":
            col3.metric("Unique region visitors", stats["unique_region_visitors"])

        st.video(stats["output_path"])
        with open(stats["output_path"], "rb") as f:
            st.download_button("Download processed video", f, file_name="people_counted_output.mp4")
else:
    st.info("Upload an image or video to get started.")
