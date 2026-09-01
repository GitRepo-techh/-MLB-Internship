import io
import time
import concurrent.futures
import numpy as np
from PIL import Image
import cv2
import streamlit as st


try:
    import pytesseract

    # On Windows, use the installed Tesseract executable.
    # On Streamlit Cloud/Linux, Tesseract is provided through PATH.
    import os

    if os.name == "nt":
        windows_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        if os.path.exists(windows_tesseract):
            pytesseract.pytesseract.tesseract_cmd = windows_tesseract

except Exception:
    pytesseract = None

try:
    import easyocr
except Exception:
    easyocr = None

try:
    from paddleocr import PaddleOCR
except Exception:
    PaddleOCR = None

try:
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor
    DOCTR_IMPORT_ERROR = None
except Exception as e:
    DocumentFile = None
    ocr_predictor = None
    DOCTR_IMPORT_ERROR = e

try:
    from rapidocr import RapidOCR
    RAPIDOCR_IMPORT_ERROR = None
except Exception as e:
    RapidOCR = None
    RAPIDOCR_IMPORT_ERROR = e



def load_easyocr_reader(lang_list=("en",)):


    if easyocr is None:
        raise ImportError("easyocr is not installed. Run: uv add easyocr")
    return easyocr.Reader(list(lang_list), gpu=False)


def load_paddleocr_model(lang="en"):

    if PaddleOCR is None:
        raise ImportError(
            "paddleocr is not installed. Run: uv add paddlepaddle paddleocr"
        )

    return PaddleOCR(
        lang=lang,
        enable_mkldnn=False
    )


def load_doctr_model():

    if ocr_predictor is None:
        raise ImportError(
            f"DocTR could not be imported. Original error: {DOCTR_IMPORT_ERROR}. "
            "Run: uv add python-doctr[torch]"
        )

    return ocr_predictor(
        det_arch="db_resnet50",
        reco_arch="crnn_vgg16_bn",
        pretrained=True
    )


def load_rapidocr_model():

    if RapidOCR is None:
        raise ImportError(
            f"rapidocr could not be imported. Original error: {RAPIDOCR_IMPORT_ERROR}. "
            "Run: uv add rapidocr onnxruntime"
        )

    return RapidOCR()


def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    # Convert a PIL RGB image to an OpenCV BGR numpy array.
    rgb_array = np.array(pil_image.convert("RGB"))
    return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
    """Convert an OpenCV BGR (or grayscale) numpy array back to a PIL image."""
    if len(cv2_image.shape) == 2:  # grayscale / single channel
        return Image.fromarray(cv2_image)
    rgb_array = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_array)


def preprocess_image(
    pil_image: Image.Image,
    grayscale: bool = True,
    denoise: bool = False,
    threshold: bool = False,
) -> Image.Image:
 
    image = pil_to_cv2(pil_image)

    if grayscale:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if denoise:
        if len(image.shape) == 2:
            image = cv2.fastNlMeansDenoising(image, h=10)
        else:
            image = cv2.fastNlMeansDenoisingColored(image, h=10, hColor=10)

    if threshold:
        if len(image.shape) != 2:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=31,
            C=15,
        )

    return cv2_to_pil(image)



def extract_text_tesseract(pil_image: Image.Image) -> str:


    if pytesseract is None:
        return "[Tesseract not available - check installation]"
    text = pytesseract.image_to_string(pil_image)
    return text.strip()


def extract_text_easyocr(pil_image: Image.Image, reader) -> str:

  
    if easyocr is None or reader is None:
        return "[EasyOCR not available - check installation]"
    image_array = np.array(pil_image.convert("RGB"))
    results = reader.readtext(image_array, detail=1)
    # results: list of (bbox, text, confidence)
    lines = [text for (_, text, _) in results]
    return "\n".join(lines).strip()


def extract_text_paddleocr(pil_image: Image.Image, model) -> str:
    """Extract text using the newer PaddleOCR API."""

    if PaddleOCR is None or model is None:
        return "[PaddleOCR not available - check installation]"

    image_array = np.array(pil_image.convert("RGB"))

    try:
        results = model.predict(image_array)

        lines = []

        for result in results:
            if hasattr(result, "json"):
                result_data = result.json
            elif isinstance(result, dict):
                result_data = result
            else:
                continue

            if callable(result_data):
                result_data = result_data()

            if not isinstance(result_data, dict):
                continue

            res = result_data.get("res", result_data)

            rec_texts = res.get("rec_texts", [])

            if rec_texts:
                lines.extend(str(text) for text in rec_texts)

        return "\n".join(lines).strip()

    except Exception as e:
        return f"[PaddleOCR error: {e}]"


def extract_text_doctr(pil_image: Image.Image, model) -> str:

    if ocr_predictor is None or model is None:
        return "[DocTR not available - check installation]"
    buffer = io.BytesIO()
    pil_image.convert("RGB").save(buffer, format="PNG")
    buffer.seek(0)
    doc = DocumentFile.from_images(buffer.read())
    result = model(doc)
    lines = []
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                words = [word.value for word in line.words]
                lines.append(" ".join(words))
    return "\n".join(lines).strip()


def extract_text_rapidocr(pil_image: Image.Image, engine) -> str:

    if RapidOCR is None or engine is None:
        return "[RapidOCR not available - check installation]"

    image_array = pil_to_cv2(pil_image)

    try:
        result = engine(image_array)
        texts = result.txts if hasattr(result, "txts") and result.txts else []
        return "\n".join(str(t) for t in texts).strip()
    except Exception as e:
        return f"[RapidOCR error: {e}]"


def run_ocr(engine_name: str, pil_image: Image.Image, engine_instance=None) -> str:
   
    if engine_name == "Tesseract":
        return extract_text_tesseract(pil_image)
    elif engine_name == "EasyOCR":
        return extract_text_easyocr(pil_image, engine_instance)
    elif engine_name == "PaddleOCR":
        return extract_text_paddleocr(pil_image, engine_instance)
    elif engine_name == "DocTR":
        return extract_text_doctr(pil_image, engine_instance)
    elif engine_name == "RapidOCR":
        return extract_text_rapidocr(pil_image, engine_instance)
    else:
        return "[Unknown OCR engine selected]"


def run_ocr_timed(engine_name: str, pil_image: Image.Image, engine_instance=None):
    """
    Same as run_ocr, but also returns how long extraction took (in seconds).
    Used to show per-document extraction time in the UI, including when
    processing multiple documents concurrently.
    """
    start_time = time.perf_counter()
    text = run_ocr(engine_name, pil_image, engine_instance)
    elapsed_seconds = time.perf_counter() - start_time
    return text, elapsed_seconds


def _process_one_document(file_name, pil_image, engine_name, engine_instance, preprocess_kwargs):
    """
    Worker function: preprocess + extract text + time it, for a single
    document. Designed to be safe to call from multiple threads at once
    (each call operates on its own image, no shared mutable state).
    """
    processed_image = preprocess_image(pil_image, **preprocess_kwargs)
    extracted_text, elapsed_seconds = run_ocr_timed(engine_name, processed_image, engine_instance)
    return {
        "file_name": file_name,
        "original_image": pil_image,
        "processed_image": processed_image,
        "extracted_text": extracted_text,
        "elapsed_seconds": elapsed_seconds,
    }


def process_documents_multithreaded(
    uploaded_files,
    engine_name: str,
    engine_instance,
    preprocess_kwargs,
    max_workers: int = 4,
):
    """
    Preprocess and run OCR on multiple uploaded documents concurrently
    using a thread pool, so a batch of documents extracts faster than
    running them one at a time in sequence.

    uploaded_files: list of (file_name, PIL.Image) tuples.
    Returns: (results, total_elapsed_seconds) where results is a list of
    dicts (see _process_one_document), in the SAME order as uploaded_files.
    """
    total_start = time.perf_counter()
    results_by_name = {}

    worker_count = min(max_workers, len(uploaded_files)) or 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_to_name = {
            executor.submit(
                _process_one_document,
                file_name,
                pil_image,
                engine_name,
                engine_instance,
                preprocess_kwargs,
            ): file_name
            for file_name, pil_image in uploaded_files
        }
        for future in concurrent.futures.as_completed(future_to_name):
            result = future.result()
            results_by_name[result["file_name"]] = result

    # Preserve the original upload order in the returned list.
    ordered_results = [results_by_name[name] for name, _ in uploaded_files]
    total_elapsed_seconds = time.perf_counter() - total_start
    return ordered_results, total_elapsed_seconds