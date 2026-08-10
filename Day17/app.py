import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io




st.set_page_config(
    page_title="OpenCV Image Processing Lab",
    page_icon="🖼️",
    layout="wide"
)



def uploaded_file_to_cv2(uploaded_file):

   
    bytes_data = uploaded_file.getvalue()
    np_array = np.frombuffer(bytes_data, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Could not read the uploaded image.")

    return image


def cv2_to_rgb(image):

  
    if len(image.shape) == 2:
        return image

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def image_to_bytes(image):


    success, encoded = cv2.imencode(".png", image)

    if not success:
        return None

    return encoded.tobytes()


def display_result(image, caption="Result"):


    st.image(
        cv2_to_rgb(image),
        caption=caption,
        use_container_width=True
    )


# ============================================================
# DOCUMENT ENHANCEMENT FUNCTIONS
# ============================================================

def find_document_contour(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    edged = cv2.Canny(
        blurred,
        50,
        150
    )

    edged = cv2.dilate(
        edged,
        None,
        iterations=1
    )

    contours, _ = cv2.findContours(
        edged.copy(),
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    contours = sorted(
        contours,
        key=cv2.contourArea,
        reverse=True
    )[:10]

    for c in contours:

        peri = cv2.arcLength(c, True)

        approx = cv2.approxPolyDP(
            c,
            0.02 * peri,
            True
        )

        if len(approx) == 4:

            area = cv2.contourArea(approx)

            if area > 0.1 * img.shape[0] * img.shape[1]:
                return approx.reshape(4, 2).astype(np.float32)

    return None


def order_points(pts):

    rect = np.zeros(
        (4, 2),
        dtype=np.float32
    )

    s = pts.sum(axis=1)

    rect[0] = pts[np.argmin(s)]   # top-left
    rect[2] = pts[np.argmax(s)]   # bottom-right

    diff = np.diff(
        pts,
        axis=1
    )

    rect[1] = pts[np.argmin(diff)]   # top-right
    rect[3] = pts[np.argmax(diff)]   # bottom-left

    return rect


def perspective_correct(
    img,
    contour,
    out_w=400,
    out_h=None
):

    if out_h is None:
        out_h = int(out_w * 1.414)

    pts1 = order_points(contour)

    pts2 = np.float32([
        [0, 0],
        [out_w, 0],
        [out_w, out_h],
        [0, out_h]
    ])

    matrix = cv2.getPerspectiveTransform(
        pts1,
        pts2
    )

    return cv2.warpPerspective(
        img,
        matrix,
        (out_w, out_h)
    )


def convert_grayscale(img):

    return cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )


def denoise(img):

    return cv2.bilateralFilter(
        img,
        d=9,
        sigmaColor=75,
        sigmaSpace=75
    )


def adjust_brightness_contrast(
    img,
    alpha=1.3,
    beta=15
):

    return cv2.convertScaleAbs(
        img,
        alpha=alpha,
        beta=beta
    )


def sharpen(img):

    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    return cv2.filter2D(
        img,
        -1,
        kernel
    )


def process_document(img):

    stages = {}

    # Original
    stages["original"] = img.copy()

    # Perspective correction
    contour = find_document_contour(img)

    if contour is not None:

        corrected = perspective_correct(
            img,
            contour
        )

        perspective_found = True

    else:

        corrected = img.copy()

        perspective_found = False

    stages["perspective_corrected"] = corrected

    # Grayscale
    gray = convert_grayscale(corrected)

    stages["grayscale"] = gray

    # Denoising
    denoised = denoise(gray)

    stages["denoised"] = denoised

    # Brightness / contrast
    bright_contrast = adjust_brightness_contrast(
        denoised,
        alpha=1.3,
        beta=15
    )

    stages["brightness_contrast"] = bright_contrast

    # Sharpen
    final = sharpen(bright_contrast)

    stages["final_enhanced"] = final

    stages["perspective_found"] = perspective_found

    return stages


# ============================================================
# CODING PRACTICE TASKS
# ============================================================

def translate_image(image, tx, ty):

    h, w = image.shape[:2]

    matrix = np.float32([
        [1, 0, tx],
        [0, 1, ty]
    ])

    return cv2.warpAffine(
        image,
        matrix,
        (w, h)
    )


def rotate_image(image, angle, scale=1.0):

    h, w = image.shape[:2]

    center = (
        w // 2,
        h // 2
    )

    matrix = cv2.getRotationMatrix2D(
        center,
        angle,
        scale
    )

    return cv2.warpAffine(
        image,
        matrix,
        (w, h)
    )


def scale_image(image, scale):

    return cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC
    )


def affine_transformation(image):

    h, w = image.shape[:2]

    pts1 = np.float32([
        [0, 0],
        [w - 1, 0],
        [0, h - 1]
    ])

    pts2 = np.float32([
        [0, 0],
        [w - 1, 50],
        [50, h - 1]
    ])

    matrix = cv2.getAffineTransform(
        pts1,
        pts2
    )

    return cv2.warpAffine(
        image,
        matrix,
        (w, h)
    )


def perspective_transformation(image):

    h, w = image.shape[:2]

    margin = int(min(h, w) * 0.15)

    pts1 = np.float32([
        [margin, margin],
        [w - margin, margin],
        [w - margin, h - margin],
        [margin, h - margin]
    ])

    pts2 = np.float32([
        [0, 0],
        [w, 0],
        [w, h],
        [0, h]
    ])

    matrix = cv2.getPerspectiveTransform(
        pts1,
        pts2
    )

    return cv2.warpPerspective(
        image,
        matrix,
        (w, h)
    )


def brightness(image, value):

    return cv2.convertScaleAbs(
        image,
        alpha=1.0,
        beta=value
    )


def contrast(image, value):

    return cv2.convertScaleAbs(
        image,
        alpha=value,
        beta=0
    )


def blurring(image, blur_type):

    if blur_type == "Gaussian":

        return cv2.GaussianBlur(
            image,
            (13, 13),
            sigmaX=8,
            sigmaY=5
        )

    elif blur_type == "Median":

        return cv2.medianBlur(
            image,
            23
        )

    else:

        return cv2.bilateralFilter(
            image,
            d=9,
            sigmaColor=198,
            sigmaSpace=198
        )


def sharpening(image, strength):

    kernel = np.array([
        [0, -1, 0],
        [-1, strength, -1],
        [0, -1, 0]
    ])

    return cv2.filter2D(
        image,
        -1,
        kernel
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🖼️ OpenCV Image Lab")

page = st.sidebar.radio(
    "Choose a task",
    [
        "📄 Document Enhancement",
        "🔄 Translation",
        "🔃 Rotation",
        "📐 Scaling",
        "🔷 Affine Transformation",
        "📄 Perspective Transformation",
        "☀️ Brightness",
        "🎚️ Contrast",
        "🌫️ Blurring",
        "✨ Sharpening",
        "🏆 Challenge Task"
    ]
)


# ============================================================
# IMAGE UPLOAD
# ============================================================

st.title("🖼️ OpenCV Image Processing Lab")

st.write(
    "Upload an image and experiment with the OpenCV operations "
    "from your Day 17 project."
)

uploaded_file = st.file_uploader(
    "Upload an image",
    type=[
        "jpg",
        "jpeg",
        "png"
    ]
)


# ============================================================
# DOCUMENT ENHANCEMENT
# ============================================================

if page == "📄 Document Enhancement":

    st.header("📄 Document Image Enhancement Tool")

    st.write(
        "This pipeline performs:"
    )

    st.write(
        "Perspective correction → Grayscale → "
        "Noise reduction → Brightness/Contrast → Sharpening"
    )

    if uploaded_file is not None:

        image = uploaded_file_to_cv2(
            uploaded_file
        )

        stages = process_document(image)

        if stages["perspective_found"]:

            st.success(
                "Document contour detected. "
                "Perspective correction was applied."
            )

        else:

            st.warning(
                "No document contour was detected. "
                "The original image was used."
            )

        col1, col2 = st.columns(2)

        with col1:

            display_result(
                stages["original"],
                "Original"
            )

            display_result(
                stages["perspective_corrected"],
                "Perspective Corrected"
            )

            display_result(
                stages["grayscale"],
                "Grayscale"
            )

        with col2:

            display_result(
                stages["denoised"],
                "Denoised"
            )

            display_result(
                stages["brightness_contrast"],
                "Brightness + Contrast"
            )

            display_result(
                stages["final_enhanced"],
                "Final Enhanced"
            )

        st.download_button(
            label="⬇️ Download Enhanced Image",
            data=image_to_bytes(
                stages["final_enhanced"]
            ),
            file_name="enhanced_document.png",
            mime="image/png"
        )


# ============================================================
# TRANSLATION
# ============================================================

elif page == "🔄 Translation":

    st.header("🔄 Translate Image")

    if uploaded_file is not None:

        image = uploaded_file_to_cv2(
            uploaded_file
        )

        tx = st.slider(
            "Horizontal translation",
            -500,
            500,
            129
        )

        ty = st.slider(
            "Vertical translation",
            -500,
            500,
            100
        )

        result = translate_image(
            image,
            tx,
            ty
        )

        col1, col2 = st.columns(2)

        with col1:
            display_result(
                image,
                "Original"
            )

        with col2:
            display_result(
                result,
                "Translated"
            )

        st.download_button(
            "⬇️ Download Result",
            image_to_bytes(result),
            "translated.png",
            "image/png"
        )


# ============================================================
# ROTATION
# ============================================================

elif page == "🔃 Rotation":

    st.header("🔃 Rotate Image")

    if uploaded_file is not None:

        image = uploaded_file_to_cv2(
            uploaded_file
        )

        angle = st.slider(
            "Rotation angle",
            -180,
            180,
            45
        )

        scale = st.slider(
            "Scale",
            0.1,
            3.0,
            1.0,
            0.1
        )

        result = rotate_image(
            image,
            angle,
            scale
        )

        col1, col2 = st.columns(2)

        with col1:
            display_result(
                image,
                "Original"
            )

        with col2:
            display_result(
                result,
                f"Rotated {angle}°"
            )

        st.download_button(
            "⬇️ Download Result",
            image_to_bytes(result),
            "rotated.png",
            "image/png"
        )


# ============================================================
# SCALING
# ============================================================

elif page == "📐 Scaling":

    st.header("📐 Scale Image")

    if uploaded_file is not None:

        image = uploaded_file_to_cv2(
            uploaded_file
        )

        scale = st.slider(
            "Scale factor",
            0.1,
            3.0,
            1.0,
            0.1
        )

        result = scale_image(
            image,
            scale
        )

        col1, col2 = st.columns(2)

        with col1:
            display_result(
                image,
                "Original"
            )

        with col2:
            display_result(
                result,
                f"Scaled ×{scale}"
            )

        st.download_button(
            "⬇️ Download Result",
            image_to_bytes(result),
            "scaled.png",
            "image/png"
        )


# ============================================================
# AFFINE TRANSFORMATION
# ============================================================

elif page == "🔷 Affine Transformation":

    st.header("🔷 Affine Transformation")

    if uploaded_file is not None:

        image = uploaded_file_to_cv2(
            uploaded_file
        )

        result = affine_transformation(
            image
        )

        col1, col2 = st.columns(2)

        with col1:
            display_result(
                image,
                "Original"
            )

        with col2:
            display_result(
                result,
                "Affine Transformation"
            )

        st.download_button(
            "⬇️ Download Result",
            image_to_bytes(result),
            "affine.png",
            "image/png"
        )


# ============================================================
# PERSPECTIVE TRANSFORMATION
# ============================================================

elif page == "📄 Perspective Transformation":

    st.header("📄 Perspective Transformation")

    st.info(
        "This automatically applies a perspective transformation "
        "using four points around the image."
    )

    if uploaded_file is not None:

        image = uploaded_file_to_cv2(
            uploaded_file
        )

        result = perspective_transformation(
            image
        )

        col1, col2 = st.columns(2)

        with col1:
            display_result(
                image,
                "Original"
            )

        with col2:
            display_result(
                result,
                "Perspective Transformed"
            )

        st.download_button(
            "⬇️ Download Result",
            image_to_bytes(result),
            "perspective.png",
            "image/png"
        )


# ============================================================
# BRIGHTNESS
# ============================================================

elif page == "☀️ Brightness":

    st.header("☀️ Adjust Brightness")

    if uploaded_file is not None:

        image = uploaded_file_to_cv2(
            uploaded_file
        )

        value = st.slider(
            "Brightness",
            -100,
            100,
            50
        )

        result = brightness(
            image,
            value
        )

        col1, col2 = st.columns(2)

        with col1:
            display_result(
                image,
                "Original"
            )

        with col2:
            display_result(
                result,
                f"Brightness: {value}"
            )

        st.download_button(
            "⬇️ Download Result",
            image_to_bytes(result),
            "brightness.png",
            "image/png"
        )


# ============================================================
# CONTRAST
# ============================================================

elif page == "🎚️ Contrast":

    st.header("🎚️ Adjust Contrast")

    if uploaded_file is not None:

        image = uploaded_file_to_cv2(
            uploaded_file
        )

        value = st.slider(
            "Contrast",
            0.1,
            3.0,
            1.5,
            0.1
        )

        result = contrast(
            image,
            value
        )

        col1, col2 = st.columns(2)

        with col1:
            display_result(
                image,
                "Original"
            )

        with col2:
            display_result(
                result,
                f"Contrast: {value}"
            )

        st.download_button(
            "⬇️ Download Result",
            image_to_bytes(result),
            "contrast.png",
            "image/png"
        )


# ============================================================
# BLURRING
# ============================================================

elif page == "🌫️ Blurring":

    st.header("🌫️ Blur Image")

    if uploaded_file is not None:

        image = uploaded_file_to_cv2(
            uploaded_file
        )

        blur_type = st.selectbox(
            "Choose blur method",
            [
                "Gaussian",
                "Median",
                "Bilateral"
            ]
        )

        result = blurring(
            image,
            blur_type
        )

        col1, col2 = st.columns(2)

        with col1:
            display_result(
                image,
                "Original"
            )

        with col2:
            display_result(
                result,
                f"{blur_type} Blur"
            )

        st.download_button(
            "⬇️ Download Result",
            image_to_bytes(result),
            "blurred.png",
            "image/png"
        )


# ============================================================
# SHARPENING
# ============================================================

elif page == "✨ Sharpening":

    st.header("✨ Sharpen Image")

    if uploaded_file is not None:

        image = uploaded_file_to_cv2(
            uploaded_file
        )

        strength = st.slider(
            "Sharpening strength",
            3,
            15,
            5
        )

        result = sharpening(
            image,
            strength
        )

        col1, col2 = st.columns(2)

        with col1:
            display_result(
                image,
                "Original"
            )

        with col2:
            display_result(
                result,
                "Sharpened"
            )

        st.download_button(
            "⬇️ Download Result",
            image_to_bytes(result),
            "sharpened.png",
            "image/png"
        )


# ============================================================
# CHALLENGE TASK
# ============================================================

elif page == "🏆 Challenge Task":

    st.header("🏆 Challenge Task")

    st.write(
        "Upload up to 5 tilted document images. "
        "The application will show:"
    )

    st.write(
        "Original → Perspective Corrected → Final Enhanced"
    )

    files = st.file_uploader(
        "Upload 5 tilted document images",
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        accept_multiple_files=True
    )

    if files:

        if len(files) > 5:

            st.warning(
                "Please upload a maximum of 5 images."
            )

        else:

            for index, uploaded in enumerate(files):

                st.divider()

                st.subheader(
                    f"Document {index + 1}: {uploaded.name}"
                )

                image = uploaded_file_to_cv2(
                    uploaded
                )

                stages = process_document(
                    image
                )

                if stages["perspective_found"]:

                    st.success(
                        "Perspective correction detected."
                    )

                else:

                    st.warning(
                        "No document contour detected. "
                        "Original image was used."
                    )

                col1, col2, col3 = st.columns(3)

                with col1:

                    display_result(
                        stages["original"],
                        "1. Original"
                    )

                with col2:

                    display_result(
                        stages["perspective_corrected"],
                        "2. Perspective Corrected"
                    )

                with col3:

                    display_result(
                        stages["final_enhanced"],
                        "3. Final Enhanced"
                    )

                st.download_button(
                    "⬇️ Download Enhanced Image",
                    image_to_bytes(
                        stages["final_enhanced"]
                    ),
                    f"{uploaded.name}_enhanced.png",
                    "image/png",
                    key=f"download_{index}"
                )

    else:

        st.info(
            "Upload your 5 tilted document images above."
        )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "Day 17 — OpenCV Image Processing Project"
)

st.sidebar.caption(
    "Document Enhancement + Coding Practice"
)