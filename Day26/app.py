import io
import cv2
import numpy as np
import streamlit as st
from PIL import Image

from segementation_script import (
    to_grayscale,
    binary_threshold,
    adaptive_threshold,
    otsu_threshold,
    watershed_segmentation,
    remove_background_grabcut,
)

st.set_page_config(page_title="Document & Object Segmentation Tool", layout="wide")

# Light ivory theme (overrides default Streamlit white) + soft card styling.
# Colors also live in .streamlit/config.toml, this CSS adds the card/border polish.
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F5F1E8;
    }
    section[data-testid="stSidebar"] {
        background-color: #EDE6D8;
    }
    div[data-testid="stFileUploader"], div[data-testid="stImage"] {
        background-color: #FFFDF8;
        border: 1px solid #DCD3BF;
        border-radius: 10px;
        padding: 12px;
    }
    .stButton > button, .stDownloadButton > button {
        background-color: #2E7D6B;
        color: #FFFDF8;
        border-radius: 8px;
        border: none;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #256456;
        color: #FFFDF8;
    }
    h1, h2, h3 {
        color: #2B2B28;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📄 Document & Object Segmentation Tool")
st.caption("Day 26 — Upload an image, choose a segmentation method, and download the result.")

METHODS = [
    "Binary Thresholding",
    "Adaptive Thresholding",
    "Otsu Thresholding",
    "Watershed (touching objects)",
    "GrabCut (foreground/background)",
]

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "bmp", "webp"])
method = st.selectbox("Segmentation method", METHODS)

# extra controls per method
if method == "Binary Thresholding":
    thresh_val = st.slider("Threshold value", 0, 255, 127)
elif method == "Adaptive Thresholding":
    block_size = st.slider("Block size (odd)", 3, 51, 11, step=2)
    c_val = st.slider("C (constant subtracted)", -10, 10, 2)

if uploaded_file is not None:
    pil_img = Image.open(uploaded_file).convert("RGB")
    img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(pil_img, use_container_width=True)

    # run selected method
    is_color_output = False
    if method == "Binary Thresholding":
        gray = to_grayscale(img_bgr)
        result = binary_threshold(gray, thresh_val=thresh_val)
    elif method == "Adaptive Thresholding":
        gray = to_grayscale(img_bgr)
        result = adaptive_threshold(gray, block_size=block_size, c=c_val)
    elif method == "Otsu Thresholding":
        gray = to_grayscale(img_bgr)
        result, otsu_val = otsu_threshold(gray)
        st.info(f"Otsu auto-selected threshold: {int(otsu_val)}")
    elif method == "Watershed (touching objects)":
        result, _ = watershed_segmentation(img_bgr)
        is_color_output = True
    else:  # GrabCut
        result, _ = remove_background_grabcut(img_bgr)
        is_color_output = True

    with col2:
        st.subheader("Segmented Output")
        if is_color_output:
            display_img = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        else:
            display_img = result
        st.image(display_img, use_container_width=True, clamp=True)

    # prepare download
    if is_color_output:
        out_pil = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    else:
        out_pil = Image.fromarray(result)

    buf = io.BytesIO()
    out_pil.save(buf, format="PNG")

    st.download_button(
        label="⬇️ Download segmented image",
        data=buf.getvalue(),
        file_name=f"segmented_{method.split()[0].lower()}.png",
        mime="image/png",
    )
else:
    st.info("Upload an image to get started.")