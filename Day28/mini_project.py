import os
import tempfile
import subprocess
import shutil

import cv2
import streamlit as st
from ultralytics import YOLO


# ============================================================
# PATHS / SETTINGS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# yolov8n.pt should be in the same folder as app.py
MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")

CONF_THRESHOLD = 0.35


TRACKER_OPTIONS = {
    "ByteTrack (fast, motion-only)": "bytetrack.yaml",
    "BoT-SORT (robust to occlusion)": "botsort.yaml",
}


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model(path: str) -> YOLO:
    return YOLO(path)


# ============================================================
# CONVERT VIDEO TO BROWSER-FRIENDLY H264
# ============================================================

def convert_to_h264(input_path: str, output_path: str) -> str:

    # Check whether FFmpeg exists
    if shutil.which("ffmpeg") is None:

        st.error(
            "FFmpeg is not installed or could not be found."
        )

        return input_path

    try:

        result = subprocess.run(
            [
                "ffmpeg",
                "-y",

                # Input
                "-i",
                input_path,

                # H.264 video
                "-c:v",
                "libx264",

                # Encoding speed
                "-preset",
                "fast",

                # Quality
                "-crf",
                "23",

                # Browser-compatible pixel format
                "-pix_fmt",
                "yuv420p",

                # Audio
                "-c:a",
                "aac",

                "-b:a",
                "128k",

                # Allow video to start playing before
                # the entire file is downloaded
                "-movflags",
                "+faststart",

                # Output
                output_path,
            ],

            check=True,

            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,

            text=True,
        )

        # Make sure the output file exists
        if not os.path.exists(output_path):

            st.error(
                "FFmpeg finished but did not create the output video."
            )

            return input_path

        # Make sure the output isn't empty
        if os.path.getsize(output_path) == 0:

            st.error(
                "FFmpeg created an empty video file."
            )

            return input_path

        return output_path

    except subprocess.CalledProcessError as e:

        st.error(
            "FFmpeg failed to convert the video."
        )

        # Display FFmpeg error for debugging
        if e.stderr:
            st.code(e.stderr)

        return input_path


# ============================================================
# RUN OBJECT TRACKING
# ============================================================

def run_tracking(
    model: YOLO,
    video_path: str,
    output_path: str,
    tracker_yaml: str,
):

    # --------------------------------------------------------
    # Read video information
    # --------------------------------------------------------

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():

        raise RuntimeError(
            "Could not open the uploaded video."
        )

    fps = cap.get(cv2.CAP_PROP_FPS) or 25

    width = int(
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    ) or 1

    cap.release()


    # --------------------------------------------------------
    # Create video writer
    # --------------------------------------------------------

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height),
    )

    # Make sure OpenCV successfully created writer
    if not writer.isOpened():

        raise RuntimeError(
            f"Could not create output video.\n"
            f"Resolution: {width}x{height}\n"
            f"FPS: {fps}"
        )


    # --------------------------------------------------------
    # Tracking variables
    # --------------------------------------------------------

    unique_ids = set()

    log_rows = []


    # --------------------------------------------------------
    # Progress bar
    # --------------------------------------------------------

    progress = st.progress(
        0,
        text="Running tracking..."
    )


    # --------------------------------------------------------
    # YOLO tracking
    # --------------------------------------------------------

    results = model.track(

        source=video_path,

        conf=CONF_THRESHOLD,

        tracker=tracker_yaml,

        persist=True,

        stream=True,

        verbose=False,
    )


    # --------------------------------------------------------
    # Process frames
    # --------------------------------------------------------

    for frame_idx, result in enumerate(results):

        frame = result.orig_img

        boxes = result.boxes


        # ----------------------------------------------------
        # Check detections
        # ----------------------------------------------------

        if (
            boxes is not None
            and boxes.id is not None
        ):

            ids = (
                boxes.id
                .int()
                .cpu()
                .tolist()
            )

            xyxy = (
                boxes.xyxy
                .cpu()
                .tolist()
            )

            confs = (
                boxes.conf
                .cpu()
                .tolist()
            )

            clss = (
                boxes.cls
                .int()
                .cpu()
                .tolist()
            )


            # ------------------------------------------------
            # Process each detected object
            # ------------------------------------------------

            for (
                box,
                obj_id,
                conf,
                cls_id
            ) in zip(
                xyxy,
                ids,
                confs,
                clss
            ):

                # Add ID to unique set
                unique_ids.add(obj_id)


                # Get class name
                class_name = model.names[cls_id]


                # Bounding box coordinates
                x1, y1, x2, y2 = map(
                    int,
                    box
                )


                # Label
                label = (
                    f"ID {obj_id} | "
                    f"{class_name} "
                    f"{conf:.2f}"
                )


                # ------------------------------------------------
                # Draw bounding box
                # ------------------------------------------------

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2,
                )


                # ------------------------------------------------
                # Draw label
                # ------------------------------------------------

                cv2.putText(
                    frame,

                    label,

                    (
                        x1,
                        max(y1 - 8, 15)
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.55,

                    (0, 255, 0),

                    2,
                )


                # ------------------------------------------------
                # Store detection information
                # ------------------------------------------------

                log_rows.append(
                    {
                        "frame": frame_idx,
                        "id": obj_id,
                        "class": class_name,
                        "confidence": round(
                            conf,
                            3
                        ),
                    }
                )


        # ----------------------------------------------------
        # Display unique object count
        # ----------------------------------------------------

        cv2.putText(
            frame,

            f"Unique objects so far: "
            f"{len(unique_ids)}",

            (15, 30),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (0, 0, 255),

            2,
        )


        # ----------------------------------------------------
        # Write processed frame
        # ----------------------------------------------------

        writer.write(frame)


        # ----------------------------------------------------
        # Update progress
        # ----------------------------------------------------

        if frame_idx % 5 == 0:

            progress.progress(

                min(
                    frame_idx / total_frames,
                    1.0
                ),

                text=(
                    f"Tracking frame "
                    f"{frame_idx}/{total_frames}"
                ),
            )


    # --------------------------------------------------------
    # Finish writing video
    # --------------------------------------------------------

    writer.release()


    progress.progress(
        1.0,
        text="Tracking complete!"
    )


    return len(unique_ids), log_rows


# ============================================================
# STREAMLIT UI
# ============================================================

st.set_page_config(
    page_title="Smart Object Tracking System",
    layout="centered",
)


st.title(
    "🎯 Smart Object Tracking System"
)


st.caption(
    "YOLO + ByteTrack / BoT-SORT — "
    "upload a video and track objects with persistent IDs."
)


# ============================================================
# TRACKER SELECTION
# ============================================================

tracker_label = st.selectbox(
    "Choose a tracker",
    list(TRACKER_OPTIONS.keys()),
)


tracker_yaml = TRACKER_OPTIONS[
    tracker_label
]


# ============================================================
# VIDEO UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload a video",
    type=[
        "mp4",
        "mov",
        "avi",
        "mkv",
    ],
)


# ============================================================
# IF VIDEO WAS UPLOADED
# ============================================================

if uploaded_file is not None:

    # --------------------------------------------------------
    # Read uploaded video
    # --------------------------------------------------------

    video_bytes = uploaded_file.getvalue()


    # --------------------------------------------------------
    # ORIGINAL VIDEO
    # --------------------------------------------------------

    st.subheader(
        "🎥 Original Video"
    )

    st.video(
        video_bytes
    )


    st.success(
        f"Video uploaded successfully: "
        f"{uploaded_file.name}"
    )


    # --------------------------------------------------------
    # RUN TRACKING BUTTON
    # --------------------------------------------------------

    if st.button(
        "🚀 Run Tracking",
        type="primary",
        use_container_width=True,
    ):

        # Temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:

            # ------------------------------------------------
            # Input video path
            # ------------------------------------------------

            input_path = os.path.join(
                tmp_dir,
                uploaded_file.name,
            )


            # ------------------------------------------------
            # Save uploaded video
            # ------------------------------------------------

            with open(
                input_path,
                "wb"
            ) as f:

                f.write(
                    video_bytes
                )


            # ------------------------------------------------
            # Output paths
            # ------------------------------------------------

            raw_output_path = os.path.join(
                tmp_dir,
                "tracked_raw.mp4",
            )

            final_output_path = os.path.join(
                tmp_dir,
                "tracked_final.mp4",
            )


            # ------------------------------------------------
            # Load YOLO model
            # ------------------------------------------------

            try:

                model = load_model(
                    MODEL_PATH
                )

            except Exception as e:

                st.error(
                    "Could not load YOLO model."
                )

                st.exception(e)

                st.stop()


            # ------------------------------------------------
            # Run tracking
            # ------------------------------------------------

            try:

                with st.spinner(
                    "Loading model and "
                    "tracking objects..."
                ):

                    unique_count, log_rows = (
                        run_tracking(
                            model,
                            input_path,
                            raw_output_path,
                            tracker_yaml,
                        )
                    )


                    # ----------------------------------------
                    # Convert to H264
                    # ----------------------------------------

                    playable_path = (
                        convert_to_h264(
                            raw_output_path,
                            final_output_path,
                        )
                    )


            except Exception as e:

                st.error(
                    "An error occurred while "
                    "processing the video."
                )

                st.exception(e)

                st.stop()


            # ------------------------------------------------
            # Check output
            # ------------------------------------------------

            if not os.path.exists(
                playable_path
            ):

                st.error(
                    "Processed video file was not created."
                )

                st.stop()


            if os.path.getsize(
                playable_path
            ) == 0:

                st.error(
                    "Processed video is empty."
                )

                st.stop()


            # ------------------------------------------------
            # Success message
            # ------------------------------------------------

            st.success(
                f"Tracking complete — "
                f"{unique_count} unique "
                f"object(s) detected."
            )


            # ------------------------------------------------
            # Debug information
            # ------------------------------------------------

            with st.expander(
                "🔧 Video Debug Information"
            ):

                st.write(
                    "Raw video size:",
                    os.path.getsize(
                        raw_output_path
                    ),
                    "bytes",
                )

                st.write(
                    "Final video size:",
                    os.path.getsize(
                        playable_path
                    ),
                    "bytes",
                )

                st.write(
                    "FFmpeg:",
                    shutil.which("ffmpeg")
                    or "Not found",
                )


            # ------------------------------------------------
            # TRACKED VIDEO
            # ------------------------------------------------

            st.subheader(
                "🎯 Tracked Video"
            )


            # Read processed video
            with open(
                playable_path,
                "rb"
            ) as f:

                tracked_video_bytes = (
                    f.read()
                )


            # Display processed video
            st.video(
                tracked_video_bytes
            )


            # ------------------------------------------------
            # DOWNLOAD
            # ------------------------------------------------

            st.download_button(
                "⬇️ Download processed video",

                data=tracked_video_bytes,

                file_name=(
                    f"tracked_"
                    f"{uploaded_file.name}"
                ),

                mime="video/mp4",

                use_container_width=True,
            )


            # ------------------------------------------------
            # DETECTION TABLE
            # ------------------------------------------------

            if log_rows:

                st.subheader(
                    "📊 Detections "
                    "(ID + confidence)"
                )


                st.dataframe(
                    log_rows,

                    use_container_width=True,

                    height=300,
                )

else:

    st.info(
        "Upload a video to get started "
        "(10–30 sec clips work best)."
    )