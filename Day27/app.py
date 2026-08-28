import streamlit as st
import cv2
import tempfile
import os
import numpy as np
from PIL import Image
from ultralytics import YOLO

# ── CONFIG ────────────────────────────────────────────────────────────
# Update this path to point at your chosen best.pt (the 23-epoch
# "helmet_detector" run had the best metrics — mAP50 93.4%)
MODEL_PATH = "C:/VsCode/-MLB-Internship/runs/detect/train-7/weights/best.pt"
CONF_THRESHOLD = 0.25

st.set_page_config(page_title="Helmet Detection", layout="wide")


@st.cache_resource
def load_model(path):
    return YOLO(path)


model = load_model(MODEL_PATH)

st.title("🪖 Custom Helmet Detection System")
st.write(
    "Upload an image or video. The model detects: **with helmet**, "
    "**without helmet**, **rider**, and **number plate**."
)

conf = st.slider("Confidence threshold", 0.0, 1.0, CONF_THRESHOLD, 0.05)

file_type = st.radio("What are you uploading?", ["Image", "Video"], horizontal=True)

# ── IMAGE FLOW ────────────────────────────────────────────────────────
if file_type == "Image":
    uploaded_file = st.file_uploader(
        "Upload an image", type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(image, use_container_width=True)

        with st.spinner("Running detection..."):
            results = model.predict(source=np.array(image), conf=conf)
            annotated = results[0].plot()  # BGR numpy array
            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

        with col2:
            st.subheader("Detected")
            st.image(annotated_rgb, use_container_width=True)

        # Detection details
        st.subheader("Detections")
        boxes = results[0].boxes
        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[cls_id]
                st.write(f"- **{class_name}** — confidence: {confidence:.2f}")
        else:
            st.write("No objects detected above the confidence threshold.")

        # Download button
        out_image = Image.fromarray(annotated_rgb)
        temp_path = os.path.join(tempfile.gettempdir(), "detected_image.jpg")
        out_image.save(temp_path)
        with open(temp_path, "rb") as f:
            st.download_button(
                label="Download processed image",
                data=f,
                file_name="detected_image.jpg",
                mime="image/jpeg",
            )

# ── VIDEO FLOW ────────────────────────────────────────────────────────
else:
    uploaded_file = st.file_uploader(
        "Upload a video", type=["mp4", "mov", "avi", "mkv"]
    )

    if uploaded_file is not None:
        # Save upload to a temp file so OpenCV can read it
        input_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        input_temp.write(uploaded_file.read())
        input_temp.close()

        st.video(input_temp.name)

        if st.button("Run detection on video"):
            cap = cv2.VideoCapture(input_temp.name)
            fps = cap.get(cv2.CAP_PROP_FPS) or 25
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            output_temp_path = os.path.join(
                tempfile.gettempdir(), "detected_video_raw.mp4"
            )
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_temp_path, fourcc, fps, (width, height))

            progress_bar = st.progress(0)
            status_text = st.empty()
            frame_count = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                results = model.predict(source=frame, conf=conf, verbose=False)
                annotated_frame = results[0].plot()
                writer.write(annotated_frame)

                frame_count += 1
                if total_frames > 0:
                    progress_bar.progress(min(frame_count / total_frames, 1.0))
                status_text.text(f"Processing frame {frame_count}/{total_frames}")

            cap.release()
            writer.release()

            # Re-encode to H.264 so it plays in-browser (mp4v often doesn't)
            final_output_path = os.path.join(
                tempfile.gettempdir(), "detected_video.mp4"
            )
            try:
                import imageio_ffmpeg
                import subprocess

                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                subprocess.run(
                    [
                        ffmpeg_exe,
                        "-y",
                        "-i", output_temp_path,
                        "-vcodec", "libx264",
                        "-pix_fmt", "yuv420p",
                        final_output_path,
                    ],
                    check=True,
                )
            except Exception as e:
                st.warning(
                    f"Re-encoding step skipped ({e}). "
                    "If the video below doesn't play, install imageio-ffmpeg."
                )
                final_output_path = output_temp_path

            status_text.text("Done!")
            st.subheader("Detected Video")
            st.video(final_output_path)

            with open(final_output_path, "rb") as f:
                st.download_button(
                    label="Download processed video",
                    data=f,
                    file_name="detected_video.mp4",
                    mime="video/mp4",
                )

        os.unlink(input_temp.name)