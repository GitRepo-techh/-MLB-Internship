import os
import tempfile
import streamlit as st
from ultralytics import YOLO

from vehicle_counter import process_video, reencode_h264, VEHICLE_CLASSES

st.set_page_config(page_title="Smart Vehicle Counting System", layout="centered")

st.title("🚗 Smart Vehicle Counting System")
st.write(
    "Upload a traffic video. The app will detect, track, and count "
    "cars, motorcycles, buses, and trucks as they cross a counting line, "
    "then let you preview and download the annotated result."
)

# ---------------------------------------------------------------------------
# Load model once (cached across reruns)
# ---------------------------------------------------------------------------
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")


model = load_model()

uploaded_file = st.file_uploader("Upload a traffic video", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    st.video(uploaded_file)

    if st.button("Run Vehicle Detection & Counting"):
        with st.spinner("Processing video... this may take a minute depending on length."):
            # Save uploaded file to a temp location
            temp_dir = tempfile.mkdtemp()
            input_path = os.path.join(temp_dir, "input.mp4")
            with open(input_path, "wb") as f:
                f.write(uploaded_file.read())

            raw_output_path = os.path.join(temp_dir, "output_raw.mp4")
            final_output_path = os.path.join(temp_dir, "output_final.mp4")

            # Run detection + tracking + counting
            counts = process_video(input_path, raw_output_path, model=model)

            # Re-encode to H.264 so Streamlit can play it back
            reencode_h264(raw_output_path, final_output_path)

        st.success("Processing complete!")

        # --- Display live stats ---
        st.subheader("Vehicle Counts")
        cols = st.columns(len(VEHICLE_CLASSES))
        for col, cls_name in zip(cols, VEHICLE_CLASSES.values()):
            col.metric(cls_name.capitalize(), counts.get(cls_name, 0))

        total = sum(counts.values())
        st.metric("Total Vehicles Counted", total)

        # --- Preview processed video ---
        st.subheader("Processed Video")
        with open(final_output_path, "rb") as f:
            video_bytes = f.read()
        st.video(video_bytes)

        # --- Download button ---
        st.download_button(
            label="Download Processed Video",
            data=video_bytes,
            file_name="vehicle_counted_output.mp4",
            mime="video/mp4",
        )
else:
    st.info("Please upload a traffic video to get started.")