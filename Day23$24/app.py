import io
import zipfile
from datetime import datetime

import streamlit as st
from PIL import Image

from ocr_utils import (
    preprocess_image,
    run_ocr_timed,
    process_documents_multithreaded,
    load_easyocr_reader,
    load_paddleocr_model,
    load_doctr_model,
    load_rapidocr_model,
)


st.set_page_config(
    page_title="Document OCR Studio",
    page_icon="📄",
    layout="wide",
)



@st.cache_resource(show_spinner="Loading EasyOCR model...")
def get_easyocr_reader():
    return load_easyocr_reader(["en"])


@st.cache_resource(show_spinner="Loading PaddleOCR model...")
def get_paddleocr_model():
    return load_paddleocr_model("en")


@st.cache_resource(show_spinner="Loading DocTR model...")
def get_doctr_model():
    return load_doctr_model()


@st.cache_resource(show_spinner="Loading RapidOCR model...")
def get_rapidocr_model():
    return load_rapidocr_model()


def get_engine_instance(engine_name: str):
    # Lazily load only the model needed for the selected engine.
    if engine_name == "EasyOCR":
        return get_easyocr_reader()
    elif engine_name == "PaddleOCR":
        return get_paddleocr_model()
    elif engine_name == "DocTR":
        return get_doctr_model()
    elif engine_name == "RapidOCR":
        return get_rapidocr_model()
    return None  # Tesseract needs no pre-loaded model


# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Settings")

engine_choice = st.sidebar.selectbox(
    "OCR Engine",
    options=["Tesseract", "EasyOCR", "PaddleOCR", "DocTR", "RapidOCR"],
    index=0,
    help="Pick which OCR engine extracts the text. Tesseract is lightest; "
     "EasyOCR, PaddleOCR, DocTR, and RapidOCR are deep-learning based and heavier.",
)

st.sidebar.markdown("### Preprocessing")
apply_grayscale = st.sidebar.checkbox("Grayscale", value=True)
apply_denoise = st.sidebar.checkbox("Denoise", value=False)
apply_threshold = st.sidebar.checkbox("Adaptive Threshold", value=False)

st.sidebar.markdown("### Batch Processing")
max_workers = st.sidebar.slider(
    "Max parallel threads",
    min_value=1,
    max_value=8,
    value=4,
    help="How many documents to process at the same time when multiple "
         "files are uploaded. Higher isn't always faster - it depends on "
         "your CPU and how heavy the selected OCR engine is.",
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Built for Day 23 - MLB Internship OCR Pipeline mini project."
)


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
st.title("📄 Document OCR Studio")
st.write(
    "Upload one or more document, receipt, invoice, or form images. The "
    "app preprocesses each one and extracts readable text using the OCR "
    "engine you select in the sidebar. Multiple documents are processed "
    "concurrently using multithreading."
)

uploaded_files = st.file_uploader(
    "Upload image(s)",
    type=["png", "jpg", "jpeg", "bmp", "tiff"],
    accept_multiple_files=True,
)

preprocess_kwargs = dict(
    grayscale=apply_grayscale,
    denoise=apply_denoise,
    threshold=apply_threshold,
)

if uploaded_files:
    st.markdown(f"**{len(uploaded_files)} document(s) uploaded.**")

    if st.button("🔍 Extract Text from All Documents", type="primary"):
        # Read all uploaded files into (name, PIL.Image) tuples up front,
        # since Streamlit's UploadedFile objects aren't safe to read
        # concurrently from multiple threads.
        loaded_images = [
            (f.name, Image.open(f)) for f in uploaded_files
        ]

        try:
            engine_instance = get_engine_instance(engine_choice)
        except ImportError as e:
            engine_instance = None
            st.error(str(e))
            st.stop()

        with st.spinner(
            f"Running {engine_choice} OCR on {len(loaded_images)} document(s) "
            f"using up to {max_workers} threads..."
        ):
            results, total_elapsed = process_documents_multithreaded(
                loaded_images,
                engine_choice,
                engine_instance,
                preprocess_kwargs,
                max_workers=max_workers,
            )

        # ---- Summary of extraction time ----
        avg_time = total_elapsed / len(results) if results else 0
        summary_cols = st.columns(3)
        summary_cols[0].metric("Documents processed", len(results))
        summary_cols[1].metric("Total time (wall clock)", f"{total_elapsed:.2f}s")
        summary_cols[2].metric("Avg. time per document", f"{avg_time:.2f}s")

        st.markdown("---")

        # ---- Per-document results ----
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for result in results:
                base_name = result["file_name"].rsplit(".", 1)[0]
                zip_file.writestr(f"{base_name}.txt", result["extracted_text"])
        zip_buffer.seek(0)

        if len(results) > 1:
            st.download_button(
                label="⬇️ Download all extracted text (.zip)",
                data=zip_buffer,
                file_name=f"ocr_results_{engine_choice.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
            )
            st.markdown("---")

        for result in results:
            with st.expander(
                f"📄 {result['file_name']}  ·  ⏱️ {result['elapsed_seconds']:.2f}s",
                expanded=(len(results) == 1),
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Original Image")
                    st.image(result["original_image"], use_container_width=True)
                with col2:
                    st.subheader("Preprocessed Image")
                    st.image(result["processed_image"], use_container_width=True)

                st.subheader("📝 Extracted Text")
                if result["extracted_text"]:
                    st.text_area(
                        "Result",
                        result["extracted_text"],
                        height=250,
                        key=f"text_{result['file_name']}",
                    )

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = result["file_name"].rsplit(".", 1)[0]
                    st.download_button(
                        label="⬇️ Download as .txt",
                        data=io.BytesIO(result["extracted_text"].encode("utf-8")),
                        file_name=f"{base_name}_ocr_{engine_choice.lower()}_{timestamp}.txt",
                        mime="text/plain",
                        key=f"download_{result['file_name']}",
                    )
                else:
                    st.warning(
                        "No text was extracted. Try a different engine or "
                        "preprocessing combination."
                    )
else:
    st.info("👆 Upload one or more images to get started.")