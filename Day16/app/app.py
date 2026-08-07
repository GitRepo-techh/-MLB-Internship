import cv2
import numpy as np
import streamlit as st



from image_ops import (
    to_grayscale,
    resize_image,
    rotate_image,
    flip_image,
    crop_image,
    draw_rectangle,
    draw_line,
    draw_circle,
    draw_polygon,
    add_text,
    encode_for_download,
)

st.set_page_config(page_title="Image Processing Toolkit", layout="wide")
st.title("🖼️ Image Processing Toolkit")


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def load_uploaded_image(uploaded_file):
    """Convert a Streamlit UploadedFile into an OpenCV BGR image."""
    file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
    return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)


def to_display(image):
    """OpenCV images are BGR; Streamlit's st.image expects RGB."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def adjust_brightness_contrast(image, brightness, contrast):
    return cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)


# ---------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------

if "original" not in st.session_state:
    st.session_state.original = None
if "image" not in st.session_state:
    st.session_state.image = None


# ---------------------------------------------------------------------
# LOAD IMAGE
# ---------------------------------------------------------------------

uploaded_file = st.sidebar.file_uploader("Load an image", type=["png", "jpg", "jpeg", "bmp"])

if uploaded_file is not None and st.session_state.original is None:
    img = load_uploaded_image(uploaded_file)
    st.session_state.original = img.copy()
    st.session_state.image = img.copy()

if st.sidebar.button("Reset to original") and st.session_state.original is not None:
    st.session_state.image = st.session_state.original.copy()

if st.session_state.image is None:
    st.info("Upload an image from the sidebar to get started.")
    st.stop()


# ---------------------------------------------------------------------
# OPERATION MENU
# ---------------------------------------------------------------------

operation = st.sidebar.selectbox(
    "Choose an operation",
    [
        "None",
        "Convert to Grayscale",
        "Resize",
        "Rotate",
        "Flip",
        "Crop",
        "Draw Shape",
        "Add Text",
        "Adjust Brightness/Contrast",
        "Compare BGR vs RGB",
    ],
)

image = st.session_state.image

# --- Grayscale --------------------------------------------------------
if operation == "Convert to Grayscale":
    if st.sidebar.button("Apply"):
        st.session_state.image = to_grayscale(image)

# --- Resize -------------------------------------------------------------
elif operation == "Resize":
    mode = st.sidebar.radio("Resize by", ["Width/Height", "Scale factor"])
    if mode == "Width/Height":
        w = st.sidebar.number_input("Width", min_value=1, value=image.shape[1])
        h = st.sidebar.number_input("Height", min_value=1, value=image.shape[0])
        if st.sidebar.button("Apply"):
            st.session_state.image = resize_image(image, width=int(w), height=int(h))
    else:
        scale = st.sidebar.slider("Scale factor", 0.1, 3.0, 1.0, 0.1)
        if st.sidebar.button("Apply"):
            st.session_state.image = resize_image(image, scale=scale)

# --- Rotate -------------------------------------------------------------
elif operation == "Rotate":
    angle = st.sidebar.selectbox("Angle", [90, 180, 270, "Custom"])
    if angle == "Custom":
        angle = st.sidebar.slider("Custom angle", -180, 180, 0)
    if st.sidebar.button("Apply"):
        st.session_state.image = rotate_image(image, angle)

# --- Flip -----------------------------------------------------------------
elif operation == "Flip":
    mode = st.sidebar.selectbox("Flip direction", ["horizontal", "vertical", "both"])
    if st.sidebar.button("Apply"):
        st.session_state.image = flip_image(image, mode)

# --- Crop -----------------------------------------------------------------
elif operation == "Crop":
    h, w = image.shape[:2]
    x1 = st.sidebar.slider("x1", 0, w, 0)
    x2 = st.sidebar.slider("x2", 0, w, w)
    y1 = st.sidebar.slider("y1", 0, h, 0)
    y2 = st.sidebar.slider("y2", 0, h, h)
    if st.sidebar.button("Apply"):
        st.session_state.image = crop_image(image, x1, y1, x2, y2)

# --- Draw Shape -------------------------------------------------------
elif operation == "Draw Shape":
    shape = st.sidebar.selectbox("Shape", ["Rectangle", "Line", "Circle", "Polygon"])
    color = st.sidebar.color_picker("Color", "#FF0000")
    # Streamlit color picker gives hex RGB -> convert to BGR tuple for OpenCV
    r, g, b = tuple(int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    bgr_color = (b, g, r)
    thickness = st.sidebar.slider("Thickness", -1, 20, 2)

    h, w = image.shape[:2]

    if shape == "Rectangle":
        x1, y1 = st.sidebar.number_input("x1", 0, w, 50), st.sidebar.number_input("y1", 0, h, 50)
        x2, y2 = st.sidebar.number_input("x2", 0, w, 200), st.sidebar.number_input("y2", 0, h, 200)
        if st.sidebar.button("Apply"):
            st.session_state.image = draw_rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), bgr_color, thickness)

    elif shape == "Line":
        x1, y1 = st.sidebar.number_input("x1", 0, w, 0), st.sidebar.number_input("y1", 0, h, 0)
        x2, y2 = st.sidebar.number_input("x2", 0, w, w), st.sidebar.number_input("y2", 0, h, h)
        if st.sidebar.button("Apply"):
            st.session_state.image = draw_line(image, (int(x1), int(y1)), (int(x2), int(y2)), bgr_color, thickness)

    elif shape == "Circle":
        cx, cy = st.sidebar.number_input("Center x", 0, w, w // 2), st.sidebar.number_input("Center y", 0, h, h // 2)
        radius = st.sidebar.slider("Radius", 1, max(w, h), 50)
        if st.sidebar.button("Apply"):
            st.session_state.image = draw_circle(image, (int(cx), int(cy)), radius, bgr_color, thickness)

    elif shape == "Polygon":
        st.sidebar.caption("Enter points as x,y pairs, one per line (e.g. 10,5)")
        raw_points = st.sidebar.text_area("Points", "10,5\n20,30\n70,20\n50,10")
        if st.sidebar.button("Apply"):
            try:
                points = [tuple(map(int, line.split(","))) for line in raw_points.strip().splitlines()]
                st.session_state.image = draw_polygon(image, points, bgr_color, thickness)
            except ValueError:
                st.sidebar.error("Could not parse points. Use format: x,y per line.")

# --- Add Text ---------------------------------------------------------
elif operation == "Add Text":
    text = st.sidebar.text_input("Text", "Hello World")
    h, w = image.shape[:2]
    x = st.sidebar.number_input("Position x", 0, w, 10)
    y = st.sidebar.number_input("Position y", 0, h, 100)
    color = st.sidebar.color_picker("Color", "#0000FF")
    r, g, b = tuple(int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    bgr_color = (b, g, r)
    font_scale = st.sidebar.slider("Font scale", 0.1, 5.0, 1.0, 0.1)
    thickness = st.sidebar.slider("Thickness", 1, 10, 2)
    if st.sidebar.button("Apply"):
        st.session_state.image = add_text(image, text, (int(x), int(y)), bgr_color, font_scale, thickness)

# --- Brightness/Contrast (bonus) ---------------------------------------
elif operation == "Adjust Brightness/Contrast":
    brightness = st.sidebar.slider("Brightness", -100, 100, 0)
    contrast = st.sidebar.slider("Contrast", 0.1, 3.0, 1.0, 0.1)
    if st.sidebar.button("Apply"):
        st.session_state.image = adjust_brightness_contrast(image, brightness, contrast)

# --- BGR vs RGB comparison (bonus) --------------------------------------
elif operation == "Compare BGR vs RGB":
    st.subheader("BGR vs RGB Comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="Raw array shown as-is (this is BGR order)", channels="BGR")
    with col2:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        st.image(rgb_image, caption="Converted to RGB", channels="RGB")




st.subheader("Original vs Processed")
col1, col2 = st.columns(2)
with col1:
    st.image(to_display(st.session_state.original), caption="Original")
with col2:
    st.image(to_display(st.session_state.image), caption="Processed")




st.sidebar.markdown("---")
file_format = st.sidebar.selectbox("Save format", [".png", ".jpg"])
img_bytes = encode_for_download(st.session_state.image, file_format)
st.sidebar.download_button(
    "Download processed image",
    data=img_bytes,
    file_name=f"processed_image{file_format}",
    mime="image/png" if file_format == ".png" else "image/jpeg",
)