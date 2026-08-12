import cv2
import numpy as np
import streamlit as st
from PIL import Image
import pandas as pd
import io


# =====================================================
# Core detection logic (same pipeline as main.py)
# =====================================================

MIN_AREA = 150  # filters out noise specks


def apply_threshold(image):
    """
    Branches between two thresholding strategies depending on
    background brightness, since a single fixed strategy fails on
    a mixed dataset (colored fills on black vs. outlines on white).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    corners = [
        gray[0, 0], gray[0, w - 1],
        gray[h - 1, 0], gray[h - 1, w - 1]
    ]
    background_is_light = np.mean(corners) > 127

    if background_is_light:
        # Light background, dark outline/fill -> invert so the shape
        # becomes the white foreground
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)
    else:
        # Dark background, bright colored fill -> luminance-weighted
        # grayscale under-detects blue/red, so use max across B,G,R
        b, g, r = cv2.split(image)
        max_channel = cv2.max(cv2.max(b, g), r)
        blurred = cv2.GaussianBlur(max_channel, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 25, 255, cv2.THRESH_BINARY)

    return binary


def find_contours(binary_image):
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in contours if cv2.contourArea(c) >= MIN_AREA]


def classify_shape(contour):
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
    vertices = len(approx)

    area = cv2.contourArea(contour)
    circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0

    if circularity > 0.85 and vertices > 6:
        return "Circle"

    shape_names = {
        3: "Triangle",
        5: "Pentagon",
        6: "Hexagon",
        7: "Heptagon",
        8: "Octagon",
        9: "Nonagon",
    }

    if vertices == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = w / float(h)
        return "Square" if 0.90 <= aspect_ratio <= 1.10 else "Rectangle"
    elif vertices in shape_names:
        return shape_names[vertices]
    elif circularity > 0.8:
        return "Circle"
    else:
        return "Polygon"


def process_image(image):
    """
    Runs the full pipeline on a single BGR image and returns
    (contour_image, final_image, results_list).
    """
    binary = apply_threshold(image)
    contours = find_contours(binary)

    contour_image = image.copy()
    final_image = image.copy()
    cv2.drawContours(contour_image, contours, -1, (45, 67, 230), 2)

    results = []
    for i, contour in enumerate(contours, start=1):
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        x, y, w, h = cv2.boundingRect(contour)
        shape = classify_shape(contour)

        cv2.drawContours(final_image, [contour], -1, (45, 67, 230), 2)
        cv2.rectangle(final_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(final_image, shape, (x, max(y - 25, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
        cv2.putText(final_image, f"A:{area:.0f} P:{perimeter:.0f}", (x, max(y - 8, 30)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        results.append({
            "#": i,
            "Shape": shape,
            "Area (px²)": round(area, 1),
            "Perimeter (px)": round(perimeter, 1),
            "Bounding Box": f"{w}x{h}",
        })

    return binary, contour_image, final_image, results


# =====================================================
# Streamlit UI
# =====================================================

st.set_page_config(page_title="Shape Detection System", page_icon="🔺", layout="wide")

st.title("🔺 Shape Detection System")
st.caption("Day 19 — MLB Internship | Contours, Shape Classification & Geometry with OpenCV")

with st.sidebar:
    st.header("About")
    st.write(
        "Upload an image containing simple geometric shapes. "
        "The app detects contours, classifies each shape, and reports "
        "its area and perimeter."
    )
    st.write("**Detectable shapes:**")
    st.write("Triangle, Square, Rectangle, Pentagon, Hexagon, Heptagon, "
             "Octagon, Nonagon, Circle, Polygon")
    st.divider()
    st.write("Works best on images with a clearly light or clearly dark "
             "background, and reasonably high-contrast shapes.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    pil_image = Image.open(uploaded_file).convert("RGB")
    image_rgb = np.array(pil_image)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    binary, contour_image, final_image, results = process_image(image_bgr)

    st.subheader("Pipeline Results")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Original**")
        st.image(image_rgb, use_container_width=True)

    with col2:
        st.markdown("**Contours Detected**")
        st.image(cv2.cvtColor(contour_image, cv2.COLOR_BGR2RGB), use_container_width=True)

    with col3:
        st.markdown("**Final — Labeled Shapes**")
        st.image(cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB), use_container_width=True)

    st.subheader("Detected Shapes")
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)

        summary = df["Shape"].value_counts().to_dict()
        st.write("**Summary:** " + ", ".join(f"{v}x {k}" for k, v in summary.items()))
    else:
        st.warning(
            "No shapes detected. Try an image with higher contrast between "
            "the shape and its background."
        )

    # Download button for the final labeled image
    result_pil = Image.fromarray(cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB))
    buf = io.BytesIO()
    result_pil.save(buf, format="PNG")
    st.download_button(
        "Download Final Labeled Image",
        data=buf.getvalue(),
        file_name="shape_detection_result.png",
        mime="image/png",
    )
else:
    st.info("Upload an image to get started, or try one of the sample shapes from your dataset.")