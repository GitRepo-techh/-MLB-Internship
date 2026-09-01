import os
import cv2
import numpy as np

from segementation_script import (
    to_grayscale,
    binary_threshold,
    adaptive_threshold,
    otsu_threshold,
    simple_foreground_mask,
)

INPUT_DIR = "input_images"
OUTPUT_DIR = "output_images"
VALID_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def process_image(path, filename):
    img_bgr = cv2.imread(path)
    if img_bgr is None:
        print(f"  [skip] could not read {filename}")
        return

    name, _ = os.path.splitext(filename)

    # 1. grayscale
    gray = to_grayscale(img_bgr)

    # 2. binary threshold
    binary = binary_threshold(gray, thresh_val=120)

    # 3. adaptive threshold
    adaptive = adaptive_threshold(gray, block_size=11, c=2)

    # 4. otsu threshold
    otsu, otsu_val = otsu_threshold(gray)

    # 6. foreground/background segmentation (quick method)
    fg_mask = simple_foreground_mask(gray)

    # 5. comparison strip: original(gray) | binary | adaptive | otsu
    labels = ["Gray", "Binary", "Adaptive", f"Otsu (T={int(otsu_val)})"]
    imgs = [gray, binary, adaptive, otsu]
    strip_imgs = []
    for label, im in zip(labels, imgs):
        im_color = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        cv2.putText(im_color, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (123, 35, 10), 2)
        strip_imgs.append(im_color)
    comparison = cv2.hconcat(strip_imgs)

    # 7. save everything
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"{name}_gray.png"), gray)
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"{name}_binary.png"), binary)
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"{name}_adaptive.png"), adaptive)
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"{name}_otsu.png"), otsu)
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"{name}_foreground_mask.png"), fg_mask)
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"{name}_comparison.png"), comparison)

    print(f"  [done] {filename} -> otsu threshold auto-picked at {int(otsu_val)}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(VALID_EXTS)]

    if not files:
        print(f"No images found in ./{INPUT_DIR}. Add at least 15 images")
        return

    print(f"Processing {len(files)} image(s)...")
    for filename in files:
        process_image(os.path.join(INPUT_DIR, filename), filename)

    print(f"\nAll outputs saved to ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()