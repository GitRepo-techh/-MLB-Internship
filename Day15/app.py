import streamlit as st
from ultralytics import YOLO
from PIL import Image
import tempfile
import os
import cv2

st.set_page_config(page_title="Drone Detection", layout="centered")

st.title("Drone Detection App")
st.write("Upload an image or video to detect objects using a YOLO model.")

# ---- Load model (cached so it doesn't reload on every interaction) ----
@st.cache_resource
def load_model():
    # swap this path to your fine-tuned drone model later if you train one
    return YOLO("yolov8n.pt")

model = load_model()

# ---- Upload ----
file = st.file_uploader(
    "Upload an image or video",
    type=["jpg", "jpeg", "png", "mp4", "mov", "avi"]
)

if file is not None:
    file_type = file.type.split("/")[0]  # "image" or "video"

    # ---------------- IMAGE ----------------
    if file_type == "image":
        image = Image.open(file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("Run Detection"):
            with st.spinner("Detecting..."):
                results = model(image)
                result = results[0]

                output_path = "temp_output.jpg"
                result.save(filename=output_path)

                st.image(output_path, caption="Detection Result", use_container_width=True)

                # show detected classes + confidence
                st.subheader("Detections")
                if len(result.boxes) == 0:
                    st.write("No objects detected.")
                else:
                    for box in result.boxes:
                        cls_id = int(box.cls[0])
                        cls_name = model.names[cls_id]
                        conf = float(box.conf[0])
                        st.write(f"- **{cls_name}** — confidence: {conf:.2f}")

                with open(output_path, "rb") as f:
                    st.download_button(
                        "Download Result Image",
                        data=f,
                        file_name="detection_result.jpg",
                        mime="image/jpeg"
                    )

    # ---------------- VIDEO ----------------
    elif file_type == "video":
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tfile.write(file.read())
        video_path = tfile.name

        st.video(video_path)

        if st.button("Run Detection"):
            with st.spinner("Processing video... this may take a while"):
                cap = cv2.VideoCapture(video_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                output_path = "temp_output_video.mp4"
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    results = model(frame, verbose=False)
                    annotated_frame = results[0].plot()
                    out.write(annotated_frame)

                cap.release()
                out.release()

                st.video(output_path)

                with open(output_path, "rb") as f:
                    st.download_button(
                        "Download Result Video",
                        data=f,
                        file_name="detection_result.mp4",
                        mime="video/mp4"
                    )

                os.unlink(video_path)