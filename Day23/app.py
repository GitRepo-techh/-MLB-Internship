import io
from datetime import datetime

import streamlit as st
from PIL import Image

from ocr_utils import (
    preprocess_image,
    run_ocr,
    load_easyocr_reader,
    load_paddleocr_model,
    load_doctr_model
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Document OCR Studio",
    page_icon="📄",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Cached model loaders - each engine's model/reader loads only once per session
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading EasyOCR model...")
def get_easyocr_reader():
    return load_easyocr_reader(["en"])


@st.cache_resource(show_spinner="Loading PaddleOCR model...")
def get_paddleocr_model():
    return load_paddleocr_model("en")


@st.cache_resource(show_spinner="Loading DocTR model...")
def get_doctr_model():
    return load_doctr_model()


def get_engine_instance(engine_name: str):
    """Lazily load only the model needed for the selected engine."""
    if engine_name == "EasyOCR":
        return get_easyocr_reader()
    elif engine_name == "PaddleOCR":
        return get_paddleocr_model()
    elif engine_name == "DocTR":
        return get_doctr_model()
    return None  # Tesseract needs no pre-loaded model


# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Settings")

engine_choice = st.sidebar.selectbox(
    "OCR Engine",
    options=["Tesseract", "EasyOCR", "PaddleOCR", "DocTR"],
    index=0,
    help="Pick which OCR engine extracts the text. Tesseract is lightest; "
         "EasyOCR/PaddleOCR/DocTR are deep-learning based and heavier.",
)

st.sidebar.markdown("### Preprocessing")
apply_grayscale = st.sidebar.checkbox("Grayscale", value=True)
apply_denoise = st.sidebar.checkbox("Denoise", value=False)
apply_threshold = st.sidebar.checkbox("Adaptive Threshold", value=False)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Built for Day 23 - MLB Internship OCR Pipeline mini project."
)


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
st.title("📄 Document OCR Studio")
st.write(
    "Upload a document, receipt, invoice, or form image. The app will "
    "preprocess it and extract the readable text using the OCR engine "
    "you select in the sidebar."
)

uploaded_file = st.file_uploader(
    "Upload an image", type=["png", "jpg", "jpeg", "bmp", "tiff"]
)

if uploaded_file is not None:
    original_image = Image.open(uploaded_file)

    processed_image = preprocess_image(
        original_image,
        grayscale=apply_grayscale,
        denoise=apply_denoise,
        threshold=apply_threshold,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Image")
        st.image(original_image, use_container_width=True)
    with col2:
        st.subheader("Preprocessed Image")
        st.image(processed_image, use_container_width=True)

    st.markdown("---")

    if st.button("🔍 Extract Text", type="primary"):
        with st.spinner(f"Running {engine_choice} OCR..."):
            try:
                engine_instance = get_engine_instance(engine_choice)
                extracted_text = run_ocr(engine_choice, processed_image, engine_instance)
            except ImportError as e:
                extracted_text = ""
                st.error(str(e))

        if extracted_text:
            st.subheader("📝 Extracted Text")
            st.text_area("Result", extracted_text, height=300)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"ocr_result_{engine_choice.lower()}_{timestamp}.txt"

            st.download_button(
                label="⬇️ Download as .txt",
                data=io.BytesIO(extracted_text.encode("utf-8")),
                file_name=file_name,
                mime="text/plain",
            )
        else:
            st.warning("No text was extracted. Try a different engine or preprocessing combination.")
else:
    st.info("👆 Upload an image to get started.")