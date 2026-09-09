import streamlit as st
import cv2
import tempfile
import os
import json

from parking_detection import ParkingDetector
from analytics import (
    calculate_statistics,
    draw_analytics_panel
)

# Resolve script base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_JSON_PATH = os.path.join(BASE_DIR, "parking_spaces.json")

st.set_page_config(
    page_title="Smart Parking AI",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Smart Parking Monitoring System")
st.write("AI-powered parking occupancy detection and real-time analytics.")

# Optional sidebar fallback for parking spaces JSON
st.sidebar.header("Configuration")
uploaded_json = st.sidebar.file_uploader("Upload parking_spaces.json", type=["json"])

uploaded_video = st.file_uploader(
    "Upload a parking lot video",
    type=["mp4", "avi", "mov", "mkv"]
)

variant = st.selectbox(
    "Select analysis mode",
    ["Parking Monitor", "Parking Analytics"]
)

confidence = st.slider(
    "Vehicle confidence",
    0.1,
    0.9,
    0.25,
    0.05
)

if uploaded_video:
    # Save uploaded video
    temp_input = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    )
    temp_input.write(uploaded_video.read())
    temp_input.close()
    input_path = temp_input.name

# Load parking spaces (UI upload > local file fallback)
    if uploaded_json is not None:
        parking_spaces = json.load(uploaded_json)
    elif os.path.exists(DEFAULT_JSON_PATH):
        with open(DEFAULT_JSON_PATH, "r") as f:
            parking_spaces = json.load(f)
    else:
        st.error(
            "⚠️ Could not find 'parking_spaces.json'. Please place it in the project folder "
            "or upload it using the sidebar."
        )
        st.stop()

    # Convert JSON data to tuple coordinates (handles both list and dict formats)
    if isinstance(parking_spaces, list):
        parking_spaces = {
            i: [tuple(point) for point in polygon]
            for i, polygon in enumerate(parking_spaces)
        }
    elif isinstance(parking_spaces, dict):
        parking_spaces = {
            key: [tuple(point) for point in polygon]
            for key, polygon in parking_spaces.items()
        }

    # Convert JSON lists to tuples
    parking_spaces = {
        key: [tuple(point) for point in polygon]
        for key, polygon in parking_spaces.items()
    }

    detector = ParkingDetector()
    cap = cv2.VideoCapture(input_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    output_path = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    ).name

    writer = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    frame_number = 0
    progress = st.progress(0)
    status = st.empty()
    video_placeholder = st.empty()

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1

        vehicles, occupied = detector.process_frame(
            frame,
            parking_spaces,
            confidence
        )

        statistics = calculate_statistics(
            len(parking_spaces),
            len(occupied)
        )

        if variant == "Parking Monitor":
            output = detector.draw_monitor(
                frame,
                parking_spaces,
                occupied,
                vehicles
            )

            cv2.putText(
                output,
                f"Total: {statistics['total']}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )
            cv2.putText(
                output,
                f"Occupied: {statistics['occupied']}",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )
            cv2.putText(
                output,
                f"Free: {statistics['available']}",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )
        else:
            output = detector.draw_monitor(
                frame,
                parking_spaces,
                occupied,
                vehicles
            )
            output = draw_analytics_panel(
                output,
                statistics,
                frame_number,
                fps
            )

        writer.write(output)

        if frame_number % 5 == 0:
            display = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
            video_placeholder.image(display, channels="RGB")

        if total_frames > 0:
            progress.progress(
                min(frame_number / total_frames, 1.0)
            )

        status.write(
            f"Processing frame {frame_number}/{total_frames}"
        )

    cap.release()
    writer.release()

    status.success("Video processing complete!")
    st.video(output_path)

    with open(output_path, "rb") as f:
        st.download_button(
            "⬇️ Download Processed Video",
            f,
            file_name="parking_result.mp4",
            mime="video/mp4"
        )