"""
Day 27 - Smart Object Detection App
Streamlit app for running pretrained YOLOv8 inference on images and videos,
with per-class colored bounding boxes, confidence display, and downloads.
"""

import io
import os
import subprocess
import tempfile

import cv2
import numpy as np
import streamlit as st
from PIL import Image
from ultralytics import YOLO
import imageio_ffmpeg


def reencode_to_h264(input_path: str, output_path: str) -> None:
    """Browsers can't play OpenCV's mp4v output — re-encode to H.264 with ffmpeg."""
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    result = subprocess.run(
        [ffmpeg_exe, "-y", "-i", input_path,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         output_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        st.error("ffmpeg re-encode failed:")
        st.code(result.stderr[-2000:])  # last part of the log, most relevant
        raise RuntimeError("ffmpeg re-encode failed")

st.set_page_config(page_title="Smart Object Detection", page_icon="🔍", layout="centered")

# ---------------------------------------------------------------------------
# Model loading (cached so it only loads once per session)
# ---------------------------------------------------------------------------
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")


model = load_model()


# ---------------------------------------------------------------------------
# Deterministic color per class (so the same class always gets the same color)
# ---------------------------------------------------------------------------
def get_class_color(cls_id: int):
    np.random.seed(cls_id)  # deterministic per class id
    return tuple(int(c) for c in np.random.randint(60, 255, size=3))


def draw_detections(frame_bgr, results, box_thickness=2, font_scale=0.6):
    """Draw boxes with a distinct color per class, plus label + confidence."""
    annotated = frame_bgr.copy()
    boxes = results.boxes

    for box in boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        color = get_class_color(cls_id)
        label = f"{model.names[cls_id]} {conf:.2f}"

        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, box_thickness)

        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
        cv2.rectangle(annotated, (x1, max(0, y1 - th - 8)), (x1 + tw + 4, y1), color, -1)
        cv2.putText(annotated, label, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 1, cv2.LINE_AA)

    return annotated


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title("🔍 Smart Object Detection")
st.caption("Pretrained YOLOv8 · Ultralytics · COCO classes")

conf_threshold = st.slider("Confidence threshold", 0.05, 1.0, 0.4, 0.05)
mode = st.radio("Input type", ["Image", "Video"], horizontal=True)

st.divider()

# ---------------------------------------------------------------------------
# Image mode
# ---------------------------------------------------------------------------
if mode == "Image":
    uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        with st.spinner("Running detection..."):
            results = model(img_array, conf=conf_threshold, verbose=False)[0]
            annotated = draw_detections(img_array, results)

        st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
                  caption="Detected Objects", use_container_width=True)

        if len(results.boxes) > 0:
            st.subheader("Detections")
            rows = [
                {"Class": model.names[int(b.cls[0])], "Confidence": f"{float(b.conf[0]):.2f}"}
                for b in results.boxes
            ]
            st.table(rows)
        else:
            st.info("No objects detected above this confidence threshold. Try lowering it.")

        success, buffer = cv2.imencode(".png", annotated)
        st.download_button(
            "⬇️ Download processed image",
            data=buffer.tobytes(),
            file_name="detected.png",
            mime="image/png",
        )

# ---------------------------------------------------------------------------
# Video mode
# ---------------------------------------------------------------------------
else:
    uploaded_vid = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "mkv"])

    if uploaded_vid:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tfile.write(uploaded_vid.read())
        tfile.flush()

        cap = cv2.VideoCapture(tfile.name)
        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

        raw_out_path = os.path.join(tempfile.gettempdir(), "detected_video_raw.mp4")
        out_path = os.path.join(tempfile.gettempdir(), "detected_video.mp4")
        writer = cv2.VideoWriter(raw_out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

        progress_bar = st.progress(0, text="Processing video...")
        frame_i = 0
        class_counts = {}

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame, conf=conf_threshold, verbose=False)[0]
            annotated_frame = draw_detections(frame, results)
            writer.write(annotated_frame)

            for b in results.boxes:
                name = model.names[int(b.cls[0])]
                class_counts[name] = class_counts.get(name, 0) + 1

            frame_i += 1
            progress_bar.progress(min(frame_i / total_frames, 1.0),
                                   text=f"Processing video... {frame_i}/{total_frames} frames")

        cap.release()
        writer.release()

        progress_bar.progress(1.0, text="Re-encoding for browser playback...")
        reencode_to_h264(raw_out_path, out_path)
        os.remove(raw_out_path)
        progress_bar.empty()

        st.success("Done!")
        st.video(out_path)

        if class_counts:
            st.subheader("Detected classes (frame count)")
            st.table([{"Class": k, "Frames detected in": v} for k, v in
                       sorted(class_counts.items(), key=lambda x: -x[1])])

        with open(out_path, "rb") as f:
            st.download_button(
                "⬇️ Download processed video",
                data=f,
                file_name="detected_video.mp4",
                mime="video/mp4",
            )

st.divider()
st.caption("Model: YOLOv8n (pretrained on COCO, 80 classes) · Built with Ultralytics + Streamlit")