import cv2
import numpy as np
import streamlit as st
from PIL import Image


def orb_detect(img_rgb, n_features=1000):
    
    # Detect ORB keypoints + descriptors on an RGB numpy image.
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    orb = cv2.ORB_create(nfeatures=n_features)
    kp, des = orb.detectAndCompute(gray, None)
    return kp, des


def match_features(des1, des2, ratio=0.75):


    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    knn_matches = bf.knnMatch(des1, des2, k=2)

    good_matches = []
    for pair in knn_matches:
        if len(pair) == 2:
            m, n = pair
            if m.distance < ratio * n.distance:
                good_matches.append(m)

    good_matches = sorted(good_matches, key=lambda m: m.distance)
    return good_matches


def process(img1, img2, n_features, ratio, max_lines):
    """Run ORB detection + matching. img1/img2 are RGB numpy arrays."""
    kp1, des1 = orb_detect(img1, n_features=n_features)
    kp2, des2 = orb_detect(img2, n_features=n_features)

    if des1 is None or des2 is None or len(kp1) == 0 or len(kp2) == 0:
        return None, len(kp1), len(kp2), 0

    good_matches = match_features(des1, des2, ratio=ratio)

    matched_img = cv2.drawMatches(
        img1, kp1, img2, kp2, good_matches[:max_lines], None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )
    return matched_img, len(kp1), len(kp2), len(good_matches)


# ---------------- Streamlit UI ----------------

st.set_page_config(page_title="Feature Matching System", layout="wide")

st.title("🔍 Image Feature Matching System")
st.write(
    "Upload two images (same object/scene from different angles, logos, "
    "book covers, landmarks, etc.) to detect and match ORB features."
)

col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("Upload Image 1", type=["jpg", "jpeg", "png"], key="img1")
with col2:
    file2 = st.file_uploader("Upload Image 2", type=["jpg", "jpeg", "png"], key="img2")

st.sidebar.header("Settings")
n_features = st.sidebar.slider("Max ORB Features", 100, 2000, 1000, step=100)
ratio = st.sidebar.slider("Lowe's Ratio Test Threshold", 0.5, 0.95, 0.75, step=0.05)
max_lines = st.sidebar.slider("Max Match Lines to Draw", 5, 200, 50, step=5)

if file1 is not None and file2 is not None:
    img1 = np.array(Image.open(file1).convert("RGB"))
    img2 = np.array(Image.open(file2).convert("RGB"))

    preview_col1, preview_col2 = st.columns(2)
    with preview_col1:
        st.image(img1, caption="Image 1", use_container_width=True)
    with preview_col2:
        st.image(img2, caption="Image 2", use_container_width=True)

    if st.button("Match Features", type="primary"):
        with st.spinner("Detecting and matching features..."):
            matched_img, kp1_count, kp2_count, good_count = process(
                img1, img2, n_features, ratio, max_lines
            )

        if matched_img is None:
            st.error("No descriptors found in one of the images — cannot match.")
        else:
            st.subheader("Matched Features")
            st.image(matched_img, use_container_width=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Keypoints in Image 1", kp1_count)
            m2.metric("Keypoints in Image 2", kp2_count)
            m3.metric("Good Matches", good_count)
else:
    st.info("Upload both images to run feature matching.")