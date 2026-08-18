import cv2
import easyocr
import streamlit as st
import numpy as np
import os
from datetime import datetime
from PIL import Image

CONFIDENCE_THRESHOLD = 0.75
output_texts = 'saved_texts/'
os.makedirs(output_texts, exist_ok=True)

st.set_page_config(page_title="Simple OCR Document Reader", layout="wide")


@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])


reader = load_reader()

st.title("Simple OCR Document Reader")
st.write("Upload an image (document, receipt, signboard, book page, or handwritten note) to extract visible text using EasyOCR.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    pil_image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(pil_image)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    with st.spinner("Extracting text..."):
        results = reader.readtext(image_bgr)

    extracted_lines = []

    for bbox, text, confidence in results:
        if confidence < CONFIDENCE_THRESHOLD:
            continue

        extracted_lines.append(text)

        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))

        cv2.rectangle(image_bgr, top_left, bottom_right, (10, 255, 10), 2)
        cv2.putText(image_bgr, text, (top_left[0], max(top_left[1] - 10, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 20, 10), 2)

    full_text = '\n'.join(extracted_lines) if extracted_lines else "No text detected above confidence threshold."
    annotated_image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Image")
        st.image(pil_image, use_container_width=True)
    with col2:
        st.subheader("Detected Text (Annotated)")
        st.image(annotated_image_rgb, use_container_width=True)

    st.subheader("Extracted Text")
    st.text_area("Result", full_text, height=250)

    base_name = os.path.splitext(uploaded_file.name)[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    text_path = os.path.join(output_texts, f"{base_name}_{timestamp}.txt")

    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    st.success(f"Text saved to: {text_path}")

    st.download_button(
        label="Download extracted text (.txt)",
        data=full_text,
        file_name=f"{base_name}_{timestamp}.txt",
        mime="text/plain"
    )
else:
    st.info("Upload an image above to get started.")