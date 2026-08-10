import cv2
import numpy as np
import os


def load_image(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {path}")
    return img


def find_document_contour(img):


    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    edged = cv2.dilate(edged, None, iterations=1)

    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            area = cv2.contourArea(approx)
            if area > 0.1 * img.shape[0] * img.shape[1]:  # ignore tiny false positives
                return approx.reshape(4, 2).astype(np.float32)
    return None


def order_points(pts):



    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left (smallest x+y)
    rect[2] = pts[np.argmax(s)]   # bottom-right (largest x+y)
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right (smallest y-x)
    rect[3] = pts[np.argmax(diff)]  # bottom-left (largest y-x)
    return rect


def perspective_correct(img, contour, out_w=400, out_h=None):

    if out_h is None:
        out_h = int(out_w * 1.414)  # A4-like ratio
    pts1 = order_points(contour)
    pts2 = np.float32([[0, 0], [out_w, 0], [out_w, out_h], [0, out_h]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(img, matrix, (out_w, out_h))


def convert_grayscale(img):

    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def denoise(img):

    # Bilateral filter: reduces noise while preserving text edges
    return cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)


def adjust_brightness_contrast(img, alpha=1.3, beta=15):

    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)


def sharpen(img):

    kernel = np.array([[0, -1, 0],
                        [-1, 5, -1],
                        [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)


def save_output(img, path):

    cv2.imwrite(path, img)


def process_document(input_path, output_path, save_intermediate=False):

    stages = {}
    img = load_image(input_path)
    stages['original'] = img

    contour = find_document_contour(img)
    if contour is not None:
        corrected = perspective_correct(img, contour)
    else:
        # No 4-point document contour found -> assume already straight, just use as-is
        corrected = img.copy()
    stages['perspective_corrected'] = corrected

    gray = convert_grayscale(corrected)
    denoised = denoise(gray)
    bright_contrast = adjust_brightness_contrast(denoised, alpha=1.3, beta=15)
    sharpened = sharpen(bright_contrast)
    stages['final_enhanced'] = sharpened

    save_output(sharpened, output_path)
    return stages if save_intermediate else None




# Challenge task:


INPUT_DIR = "input_images"
OUT_DIR = "challenge_task"
os.makedirs(OUT_DIR, exist_ok=True)

# Pick your 5 tilted images here
TILTED_IMAGES = ["image1.jpg", "image2.jpg", "image3.jpg", "image4.jpg", "image5.jpg"]


def to_3channel(img):

 
    if len(img.shape) == 2:
        return np.stack((img,) * 3, axis=-1)
    return img


def make_comparison(stages, target_h=500):
    imgs = [stages['original'], stages['perspective_corrected'], stages['final_enhanced']]
    resized = []
    for im in imgs:
        im = to_3channel(im)
        h, w = im.shape[:2]
        scale = target_h / h
        im = cv2.resize(im, (int(w * scale), target_h))
        resized.append(im)
    return np.hstack(resized)


for fname in TILTED_IMAGES:
    in_path = os.path.join(".", fname)
    if not os.path.exists(in_path):
        print(f"  SKIP (not found): {fname}")
        continue

    base = os.path.splitext(fname)[0]
    out_path = os.path.join(OUT_DIR, f"{base}_enhanced.jpg")
    stages = process_document(in_path, out_path, save_intermediate=True)

    cv2.imwrite(os.path.join(OUT_DIR, f"{base}_1_original.jpg"), stages['original'])
    cv2.imwrite(os.path.join(OUT_DIR, f"{base}_2_corrected.jpg"), stages['perspective_corrected'])
    cv2.imwrite(os.path.join(OUT_DIR, f"{base}_3_enhanced.jpg"), stages['final_enhanced'])

    comparison = make_comparison(stages)
    cv2.imwrite(os.path.join(OUT_DIR, f"{base}_comparison.jpg"), comparison)
    print(f"  Done: {fname} -> {base}_comparison.jpg")

print("Challenge task complete.")

if __name__ == "__main__":
    input_dir = r"..\..\Input images"
    output_dir = r"..\..\Output images"
    os.makedirs(output_dir, exist_ok=True)

    files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    print(f"Found {len(files)} images to process.")

    for fname in files:
        in_path = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, f"enhanced_{fname}")
        try:
            process_document(in_path, out_path)
            print(f"  Processed: {fname} -> {out_path}")
        except Exception as e:
            print(f"  FAILED: {fname} -> {e}")

    print("Done.")