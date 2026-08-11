import cv2
import numpy as np
import streamlit as st
from PIL import Image


class DocumentScanner:
    """Detects the boundary of a document (receipt/ID card) in a photo."""

    def to_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def apply_blur(self, gray_image):
        return cv2.GaussianBlur(gray_image, (15, 15), sigmaX=0)

    def detect_edges(self, blurred_image):
        return cv2.Canny(blurred_image, 30, 100)

    def clean_edges(self, edge_image):
        kernel = np.ones((9, 9), np.uint8)
        return cv2.morphologyEx(edge_image, cv2.MORPH_CLOSE, kernel, iterations=2)

    def find_document_contour(self, cleaned_edges):
        contours, _ = cv2.findContours(cleaned_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        image_area = cleaned_edges.shape[0] * cleaned_edges.shape[1]
        min_area = 0.1 * image_area

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                break

            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            if solidity < 0.85:
                continue

            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            if len(approx) == 4:
                return approx

        return contours[0]

    def draw_boundary(self, original_image, contour):
        output = original_image.copy()
        cv2.drawContours(output, [contour], -1, (0, 255, 0), 3)
        return output

    def process(self, image):
        # image: BGR numpy array, resized to a consistent width first
        target_width = 800
        h, w = image.shape[:2]
        scale = target_width / w
        image = cv2.resize(image, (target_width, int(h * scale)))

        gray = self.to_grayscale(image)
        blurred = self.apply_blur(gray)
        edges = self.detect_edges(blurred)
        cleaned = self.clean_edges(edges)
        contour = self.find_document_contour(cleaned)

        if contour is None:
            return image, edges, cleaned, None

        result = self.draw_boundary(image, contour)
        return image, edges, cleaned, result


st.set_page_config(page_title="Document Boundary Detector", layout="wide")

st.title("📄 Document Boundary Detection Tool")
st.write(
    "Upload a photo of a receipt or ID card. The app runs it through a "
    "grayscale → blur → Canny → morphology → contour pipeline to detect "
    "and outline the document's boundary."
)

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    pil_image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(pil_image)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    scanner = DocumentScanner()
    resized, edges, cleaned, result = scanner.process(image_bgr)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original")
        st.image(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB), use_container_width=True)

        st.subheader("Canny Edges")
        st.image(edges, use_container_width=True)

    with col2:
        st.subheader("After Morphological Closing")
        st.image(cleaned, use_container_width=True)

        st.subheader("Detected Boundary")
        if result is not None:
            st.image(cv2.cvtColor(result, cv2.COLOR_BGR2RGB), use_container_width=True)
        else:
            st.warning("No document boundary could be detected in this image.")

    if result is not None:
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        result_pil = Image.fromarray(result_rgb)
        import io
        buf = io.BytesIO()
        result_pil.save(buf, format="PNG")
        st.download_button(
            "Download result",
            data=buf.getvalue(),
            file_name="boundary_result.png",
            mime="image/png",
        )
else:
    st.info("Upload an image to get started.")