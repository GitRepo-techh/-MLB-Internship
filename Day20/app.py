import streamlit as st
import cv2
import numpy as np
import tempfile
import os

st.set_page_config(page_title="Day 20 - Video Edge Detection", layout="wide")

st.title("Day 20 — Real-Time Video Processing (Grayscale → Blur → Canny)")
st.write(
    "Upload a short video. The app converts every frame to grayscale, "
    "applies Gaussian Blur to reduce noise, then runs Canny Edge Detection. "
    "You can tune the parameters live and download the processed result."
)

# ---------------- Sidebar controls ----------------
st.sidebar.header("Processing Parameters")

blur_kernel = st.sidebar.slider(
    "Gaussian Blur kernel size (odd numbers only)",
    min_value=1, max_value=25, value=15, step=2
)

canny_low = st.sidebar.slider("Canny lower threshold", 0, 300, 50)
canny_high = st.sidebar.slider("Canny upper threshold", 0, 300, 90)

resize_width = st.sidebar.slider(
    "Resize width (px) — smaller = faster processing",
    min_value=160, max_value=1280, value=640, step=80
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Tip: textured/high-detail footage (rocks, water, foliage) usually needs "
    "a larger blur kernel and higher Canny thresholds to avoid a noisy edge map."
)

# ---------------- Main upload + processing ----------------
uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov", "mkv"])

def process_video(input_path, output_path, blur_k, low, high, target_w):
    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        return None, None, "Could not open the uploaded video."

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps != fps:  # 0 or NaN fallback
        fps = 20.0

    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # keep aspect ratio when resizing
    scale = target_w / orig_w
    target_h = int(orig_h * scale)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h), isColor=True)

    sample_original, sample_processed = None, None
    frame_idx = 0

    progress = st.progress(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (target_w, target_h))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        k = blur_k if blur_k % 2 == 1 else blur_k + 1  # kernel must be odd
        blurred = cv2.GaussianBlur(gray, (k, k), 0)
        canny = cv2.Canny(blurred, low, high)
        canny_bgr = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)

        out.write(canny_bgr)

        # grab a mid-video frame as the preview example
        if frame_idx == total_frames // 2:
            sample_original = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            sample_processed = cv2.cvtColor(canny_bgr, cv2.COLOR_BGR2RGB)

        frame_idx += 1
        if total_frames > 0:
            progress.progress(min(frame_idx / total_frames, 1.0))

    cap.release()
    out.release()
    progress.empty()

    return sample_original, sample_processed, {
        "fps": fps, "width": orig_w, "height": orig_h, "total_frames": total_frames
    }


if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
        tmp_in.write(uploaded_file.read())
        input_path = tmp_in.name

    output_path = input_path.replace(".mp4", "_processed.mp4")

    st.subheader("Original video")
    st.video(input_path)

    if st.button("Process video"):
        with st.spinner("Processing frames..."):
            sample_orig, sample_proc, info = process_video(
                input_path, output_path, blur_kernel, canny_low, canny_high, resize_width
            )

        if isinstance(info, str):
            st.error(info)
        else:
            st.success("Done!")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("FPS", f"{info['fps']:.1f}")
            col2.metric("Width", info["width"])
            col3.metric("Height", info["height"])
            col4.metric("Total Frames", info["total_frames"])

            st.subheader("Before / After (sample frame)")
            c1, c2 = st.columns(2)
            with c1:
                st.image(sample_orig, caption="Original frame", use_container_width=True)
            with c2:
                st.image(sample_proc, caption="Grayscale + Blur + Canny", use_container_width=True)

            st.subheader("Processed video")
            st.video(output_path)

            with open(output_path, "rb") as f:
                st.download_button(
                    "Download processed video",
                    f,
                    file_name="processed_output.mp4",
                    mime="video/mp4"
                )

st.markdown("---")

# ---------------- Example images section ----------------
st.subheader("Example results")
st.write(
    "Sample before/after frames from videos processed during this project. "
    "(Replace the images in the `examples/` folder with your own before/after "
    "screenshots pulled from your Day-20 output videos.)"
)

example_cols = st.columns(3)
example_files = [
    ("examples/example1_before.png", "examples/example1_after.png", "Video 1 — rocky stream"),
    ("examples/example2_before.png", "examples/example2_after.png", "Video 2"),
    ("examples/example3_before.png", "examples/example3_after.png", "Video 3"),
]

for col, (before_path, after_path, label) in zip(example_cols, example_files):
    with col:
        st.caption(label)
        if os.path.exists(before_path) and os.path.exists(after_path):
            st.image(before_path, caption="Before")
            st.image(after_path, caption="After")
        else:
            st.info("Add example images to the examples/ folder to show them here.")