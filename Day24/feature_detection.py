import os
import sys
import time
import cv2
import numpy as np

INPUT_DIR = "input images"
OUTPUT_DIR = "output images"


def load_image(path=None):
    """Load an image from disk, or synthesize a demo image if no path is given."""
    if path:
        img = cv2.imread(path)
        if img is None:
            raise FileNotFoundError(f"Could not read image at: {path}")
        return img

    # Synthetic demo image: some rectangles + a triangle -> gives clear corners
    demo = np.full((400, 500, 3), 30, dtype=np.uint8)
    cv2.rectangle(demo, (50, 50), (200, 200), (200, 200, 200), -1)
    cv2.rectangle(demo, (250, 100), (450, 350), (100, 180, 240), -1)
    pts = np.array([[300, 50], [400, 50], [350, 150]], np.int32)
    cv2.fillPoly(demo, [pts], (0, 200, 0))
    print("No image path given -> using a synthetic demo image instead.")
    return demo


def harris_corner_detection(img, block_size=2, ksize=3, k=0.04, thresh_ratio=0.01):
    """Classic Harris Corner Detector. Returns (annotated_image, corner_count)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_f = np.float32(gray)

    start = time.time()
    dst = cv2.cornerHarris(gray_f, blockSize=block_size, ksize=ksize, k=k)
    dst = cv2.dilate(dst, None)  # dilate to make corner markers visible
    elapsed = time.time() - start

    annotated = img.copy()
    threshold = thresh_ratio * dst.max()
    corner_mask = dst > threshold
    annotated[corner_mask] = [0, 0, 255]  # mark corners in red

    corner_count = int(np.sum(corner_mask))
    return annotated, corner_count, elapsed


def orb_keypoint_detection(img, n_features=500):
    """ORB keypoint + descriptor detection. Returns (annotated_image, kp, des, elapsed)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(nfeatures=n_features)

    start = time.time()
    kp, des = orb.detectAndCompute(gray, None)
    elapsed = time.time() - start

    annotated = cv2.drawKeypoints(
        img, kp, None, color=(0, 255, 0),
        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    )
    return annotated, kp, des, elapsed


def process_single(path, out_dir="."):
    """Run Harris + ORB detection on one image, save annotated outputs, return stats."""
    img = load_image(path)
    name = os.path.splitext(os.path.basename(path))[0] if path else "demo"

    harris_img, harris_count, harris_time = harris_corner_detection(img)
    cv2.imwrite(os.path.join(out_dir, f"{name}_harris.jpg"), harris_img)

    orb_img, kp, des, orb_time = orb_keypoint_detection(img)
    cv2.imwrite(os.path.join(out_dir, f"{name}_orb.jpg"), orb_img)

    return {
        "name": name,
        "harris_count": harris_count,
        "harris_time": harris_time,
        "orb_count": len(kp),
        "orb_time": orb_time,
    }


def print_comparison(stats):
    print(f"\n----- {stats['name']} -----")
    print(f"{'Method':<25}{'Features Found':<20}{'Time (s)':<10}")
    print(f"{'Harris Corner Detector':<25}{stats['harris_count']:<20}{stats['harris_time']:.5f}")
    print(f"{'ORB':<25}{stats['orb_count']:<20}{stats['orb_time']:.5f}")


def run_batch():
    """Process every image found in the 'input images' folder."""
    if not os.path.isdir(INPUT_DIR):
        print(f"No '{INPUT_DIR}' folder found next to this script.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    valid_ext = (".jpg", ".jpeg", ".png", ".bmp")
    files = sorted(f for f in os.listdir(INPUT_DIR) if f.lower().endswith(valid_ext))

    if not files:
        print(f"No images found in '{INPUT_DIR}'.")
        return

    print(f"Found {len(files)} image(s) in '{INPUT_DIR}'. Running Harris + ORB detection...")
    all_stats = []
    for f in files:
        stats = process_single(os.path.join(INPUT_DIR, f), out_dir=OUTPUT_DIR)
        print_comparison(stats)
        all_stats.append(stats)

    print(f"\nSaved {len(files) * 2} annotated images to '{OUTPUT_DIR}/'.")
    print("Harris  -> raw corner pixel locations only, no descriptor, NOT rotation/scale")
    print("           invariant. Good for simple corner-rich scenes.")
    print("ORB     -> keypoints WITH binary descriptors, IS rotation invariant and")
    print("           reasonably scale-tolerant. Needed for matching across images.")
    return all_stats


def main():
    # Single-image mode: python feature_detection.py path/to/image.jpg
    if len(sys.argv) > 1:
        stats = process_single(sys.argv[1])
        print_comparison(stats)
        print(f"\nSaved: {stats['name']}_harris.jpg, {stats['name']}_orb.jpg")
        return

    # Batch mode: auto-run on every image in "input images/" if that folder exists
    if os.path.isdir(INPUT_DIR):
        run_batch()
        return

    # Fallback: synthetic demo image
    stats = process_single(None)
    print_comparison(stats)
    print(f"\nSaved: {stats['name']}_harris.jpg, {stats['name']}_orb.jpg")


if __name__ == "__main__":
    main()