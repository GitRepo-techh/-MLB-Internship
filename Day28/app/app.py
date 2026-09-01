import streamlit as st
import cv2
import tempfile
import os
import numpy as np
from PIL import Image
from ultralytics import YOLO

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

# best.pt is in the same folder as this app.py file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")

CONF_THRESHOLD = 0.25

st.set_page_config(
    page_title="Helmet Detection",
    layout="wide"
)


# ─────────────────────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────────────────────

@st.cache_resource
def load_model(path):
    return YOLO(path)


# Check that model actually exists before loading it
if not os.path.exists(MODEL_PATH):
    st.error(
        "❌ Model file 'best.pt' was not found.\n\n"
        "Make sure best.pt is in the same folder as app.py."
    )
    st.stop()

try:
    model = load_model(MODEL_PATH)
except Exception as e:
    st.error(f"❌ Could not load the YOLO model: {e}")
    st.stop()


# ─────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────

st.title("🪖 Custom Helmet Detection System")

st.write(
    "Upload an image or video. The model detects: "
    "**with helmet**, **without helmet**, **rider**, and **number plate**."
)

conf = st.slider(
    "Confidence threshold",
    min_value=0.0,
    max_value=1.0,
    value=CONF_THRESHOLD,
    step=0.05
)

file_type = st.radio(
    "What are you uploading?",
    ["Image", "Video"],
    horizontal=True
)


# ─────────────────────────────────────────────────────────────
# IMAGE FLOW
# ─────────────────────────────────────────────────────────────

if file_type == "Image":

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:

        try:
            image = Image.open(uploaded_file).convert("RGB")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Original")
                st.image(image, use_container_width=True)

            with st.spinner("Running detection..."):

                # Convert PIL image to NumPy array
                image_array = np.array(image)

                results = model.predict(
                    source=image_array,
                    conf=conf,
                    verbose=False
                )

                # YOLO plot() returns BGR
                annotated = results[0].plot()

                # Convert BGR → RGB for Streamlit
                annotated_rgb = cv2.cvtColor(
                    annotated,
                    cv2.COLOR_BGR2RGB
                )

            with col2:
                st.subheader("Detected")
                st.image(
                    annotated_rgb,
                    use_container_width=True
                )

            # ─────────────────────────────────────────────
            # DETECTION DETAILS
            # ─────────────────────────────────────────────

            st.subheader("Detections")

            boxes = results[0].boxes

            if boxes is not None and len(boxes) > 0:

                for box in boxes:

                    cls_id = int(box.cls[0])
                    confidence = float(box.conf[0])

                    # Safely get class name
                    if isinstance(model.names, dict):
                        class_name = model.names.get(
                            cls_id,
                            f"Class {cls_id}"
                        )
                    else:
                        class_name = model.names[cls_id]

                    st.write(
                        f"- **{class_name}** "
                        f"— confidence: {confidence:.2f}"
                    )

            else:
                st.info(
                    "No objects detected above the "
                    "confidence threshold."
                )

            # ─────────────────────────────────────────────
            # DOWNLOAD IMAGE
            # ─────────────────────────────────────────────

            out_image = Image.fromarray(annotated_rgb)

            image_bytes = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".jpg"
            )

            image_bytes.close()

            out_image.save(
                image_bytes.name,
                format="JPEG"
            )

            with open(image_bytes.name, "rb") as f:

                st.download_button(
                    label="Download processed image",
                    data=f.read(),
                    file_name="detected_image.jpg",
                    mime="image/jpeg"
                )

            # Clean up
            try:
                os.unlink(image_bytes.name)
            except Exception:
                pass

        except Exception as e:

            st.error(
                f"❌ Error while processing the image: {e}"
            )


# ─────────────────────────────────────────────────────────────
# VIDEO FLOW
# ─────────────────────────────────────────────────────────────

else:

    uploaded_file = st.file_uploader(
        "Upload a video",
        type=["mp4", "mov", "avi", "mkv"]
    )

    if uploaded_file is not None:

        # Save uploaded video to temporary file
        input_temp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        )

        input_temp.write(uploaded_file.getbuffer())
        input_temp.close()

        st.video(input_temp.name)

        if st.button("▶ Run detection on video"):

            cap = None
            writer = None

            try:

                cap = cv2.VideoCapture(input_temp.name)

                if not cap.isOpened():
                    st.error(
                        "❌ OpenCV could not open the uploaded video."
                    )
                    st.stop()

                fps = cap.get(cv2.CAP_PROP_FPS)

                if fps <= 0:
                    fps = 25

                width = int(
                    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                )

                height = int(
                    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                )

                total_frames = int(
                    cap.get(cv2.CAP_PROP_FRAME_COUNT)
                )

                # Safety check
                if width <= 0 or height <= 0:
                    st.error(
                        "❌ Could not read the video dimensions."
                    )
                    st.stop()

                # Temporary output
                output_temp_path = os.path.join(
                    tempfile.gettempdir(),
                    "detected_video_raw.mp4"
                )

                # MP4 writer
                fourcc = cv2.VideoWriter_fourcc(
                    *"mp4v"
                )

                writer = cv2.VideoWriter(
                    output_temp_path,
                    fourcc,
                    fps,
                    (width, height)
                )

                if not writer.isOpened():
                    st.error(
                        "❌ Could not create the output video."
                    )
                    st.stop()

                progress_bar = st.progress(0)
                status_text = st.empty()

                frame_count = 0

                # ─────────────────────────────────────────
                # PROCESS FRAMES
                # ─────────────────────────────────────────

                while True:

                    ret, frame = cap.read()

                    if not ret:
                        break

                    results = model.predict(
                        source=frame,
                        conf=conf,
                        verbose=False
                    )

                    annotated_frame = results[0].plot()

                    writer.write(annotated_frame)

                    frame_count += 1

                    if total_frames > 0:

                        progress = min(frame_count / total_frames, 1.0)

                        progress_bar.progress(progress)

                        status_text.text(
                            f"Processing frame {frame_count}/{total_frames}")

                    else:

                        status_text.text(f"Processing frame {frame_count}")

# ─────────────────────────────────────────
# RELEASE VIDEO RESOURCES
# ─────────────────────────────────────────

                cap.release()
                cap = None

                writer.release()
                writer = None

                progress_bar.progress(1.0)
                status_text.text("✅ Detection complete!")

                # ─────────────────────────────────────────
                # RE-ENCODE TO H.264
                # ─────────────────────────────────────────

                final_output_path = os.path.join(
                    tempfile.gettempdir(),
                    "detected_video.mp4"
                )

                try:

                    import imageio_ffmpeg
                    import subprocess

                    ffmpeg_exe = (
                        imageio_ffmpeg.get_ffmpeg_exe()
                    )

                    subprocess.run(
                        [
                            ffmpeg_exe,
                            "-y",
                            "-i",
                            output_temp_path,
                            "-c:v",
                            "libx264",
                            "-pix_fmt",
                            "yuv420p",
                            "-movflags",
                            "+faststart",
                            final_output_path
                        ],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )

                except Exception:

                    # If FFmpeg is unavailable,
                    # use the OpenCV output instead.
                    final_output_path = (
                        output_temp_path
                    )

                    st.warning(
                        "⚠️ H.264 conversion was unavailable. "
                        "The processed video was created using "
                        "OpenCV instead."
                    )

                # ─────────────────────────────────────────
                # SHOW VIDEO
                # ─────────────────────────────────────────

                st.subheader("Detected Video")

                st.video(final_output_path)

                # ─────────────────────────────────────────
                # DOWNLOAD VIDEO
                # ─────────────────────────────────────────

                with open(
                    final_output_path,
                    "rb"
                ) as f:

                    st.download_button(
                        label="⬇ Download processed video",
                        data=f.read(),
                        file_name="detected_video.mp4",
                        mime="video/mp4"
                    )

            except Exception as e:

                st.error(
                    f"❌ Error while processing the video: {e}"
                )

            finally:

                # Always release OpenCV resources
                if cap is not None:
                    cap.release()

                if writer is not None:
                    writer.release()

        # Do not delete the input file until Streamlit
        # has finished using it for this interaction.
