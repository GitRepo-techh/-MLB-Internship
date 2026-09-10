import io
import cv2
import numpy as np
import streamlit as st
from PIL import Image


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Image Segmentation Studio",
    page_icon="🖼️",
    layout="wide",
)


# --------------------------------------------------
# IMAGE PROCESSING FUNCTIONS
# --------------------------------------------------

def pil_to_bgr(pil_image):
    """Convert PIL RGB image to OpenCV BGR format."""
    rgb = np.array(pil_image.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def to_gray(image_bgr):
    """Convert BGR image to grayscale."""
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)


def binary_threshold(gray, threshold_value):
    """Apply standard binary thresholding."""
    _, segmented = cv2.threshold(
        gray,
        threshold_value,
        255,
        cv2.THRESH_BINARY,
    )

    return segmented


def adaptive_threshold(gray, block_size, c_value):
    """Apply adaptive Gaussian thresholding."""

    # block_size must be odd and greater than 1
    if block_size <= 1:
        block_size = 3

    if block_size % 2 == 0:
        block_size += 1

    segmented = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        c_value,
    )

    return segmented


def otsu_threshold(gray):
    """Apply Otsu automatic thresholding."""

    # Reduce noise before applying Otsu
    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0,
    )

    threshold_value, segmented = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    return segmented, threshold_value


def encode_download(image):
    """Convert a grayscale OpenCV image into PNG bytes."""

    pil_image = Image.fromarray(image)

    buffer = io.BytesIO()

    pil_image.save(
        buffer,
        format="PNG",
    )

    return buffer.getvalue()


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🖼️ Image Segmentation Studio")

st.caption(
    "Binary | Adaptive | Otsu Thresholding — Day 38 Deployment Task"
)


# --------------------------------------------------
# SIDEBAR SETTINGS
# --------------------------------------------------

with st.sidebar:

    st.header("⚙️ Segmentation Settings")

    method = st.selectbox(
        "Select segmentation method",
        [
            "Binary",
            "Adaptive",
            "Otsu",
        ],
    )

    if method == "Binary":

        threshold_value = st.slider(
            "Threshold value",
            min_value=0,
            max_value=255,
            value=127,
        )

    elif method == "Adaptive":

        block_size = st.slider(
            "Block size",
            min_value=3,
            max_value=51,
            value=11,
            step=2,
        )

        c_value = st.slider(
            "C value",
            min_value=-20,
            max_value=20,
            value=2,
        )


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload an image",
    type=[
        "jpg",
        "jpeg",
        "png",
        "bmp",
    ],
)


# --------------------------------------------------
# PROCESS IMAGE
# --------------------------------------------------

if uploaded_file is not None:

    try:

        # Open uploaded image
        pil_image = Image.open(uploaded_file)

        # Convert to OpenCV format
        image_bgr = pil_to_bgr(pil_image)

        # Convert to grayscale
        gray = to_gray(image_bgr)

        # ------------------------------------------
        # APPLY SELECTED SEGMENTATION METHOD
        # ------------------------------------------

        if method == "Binary":

            segmented = binary_threshold(
                gray,
                threshold_value,
            )

            info = (
                f"Binary thresholding applied "
                f"with threshold = {threshold_value}"
            )

            filename_suffix = "binary"

        elif method == "Adaptive":

            segmented = adaptive_threshold(
                gray,
                block_size,
                c_value,
            )

            info = (
                f"Adaptive Gaussian thresholding applied "
                f"with block size = {block_size}, "
                f"C = {c_value}"
            )

            filename_suffix = "adaptive"

        else:

            segmented, otsu_value = otsu_threshold(
                gray
            )

            info = (
                f"Otsu automatically selected "
                f"threshold = {otsu_value:.1f}"
            )

            filename_suffix = "otsu"

        # ------------------------------------------
        # IMAGE INFORMATION
        # ------------------------------------------

        width, height = pil_image.size

        st.success(
            f"Image processed successfully: "
            f"{width} × {height} pixels"
        )

        # ------------------------------------------
        # DISPLAY ORIGINAL + SEGMENTED
        # ------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Original Image")

            st.image(
                pil_image,
                use_container_width=True,
            )

        with col2:

            st.subheader(
                f"Segmented Image — {method}"
            )

            st.image(
                segmented,
                use_container_width=True,
                clamp=True,
            )

        # ------------------------------------------
        # PROCESSING INFORMATION
        # ------------------------------------------

        st.info(info)

        # ------------------------------------------
        # DOWNLOAD BUTTON
        # ------------------------------------------

        png_bytes = encode_download(
            segmented
        )

        st.download_button(
            label="⬇️ Download Segmented Image",
            data=png_bytes,
            file_name=f"segmented_{filename_suffix}.png",
            mime="image/png",
        )

    except Exception as error:

        st.error(
            f"Could not process the image: {error}"
        )


# --------------------------------------------------
# INFORMATION SHOWN BEFORE UPLOAD
# --------------------------------------------------

else:

    st.info(
        "Upload an image to apply segmentation."
    )

    st.markdown(
        """
### 📚 Segmentation Methods

**Binary Thresholding**

Uses one manually selected threshold value. Pixels
above the threshold become white, while pixels below
it become black. It is fast and simple but works best
when the image has relatively uniform lighting.

**Adaptive Thresholding**

Calculates a threshold independently for different
local regions of the image. This makes it more useful
when lighting varies across the image or shadows are
present.

**Otsu Thresholding**

Automatically calculates a global threshold by finding
a value that provides good separation between the
foreground and background intensity distributions.
It does not require manual threshold selection.

### 💡 Quick Comparison

| Method | Threshold | Handles Uneven Lighting |
|---|---|---|
| Binary | Manual | ❌ Poorly |
| Adaptive | Local | ✅ Well |
| Otsu | Automatic | ❌ Limited |
        """
    )
