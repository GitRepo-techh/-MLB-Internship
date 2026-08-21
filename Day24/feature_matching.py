import os
import sys
import cv2
import numpy as np


INPUT_DIR = "input images"
OUTPUT_DIR = "output images"
COMPARISON_DIR = "comparison"

def load_pair(path1, path2):
    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)

    if img1 is None or img2 is None:
        raise FileNotFoundError(
            "Could not read one or both image paths."
        )

    return img1, img2


def orb_detect(img, n_features=1000):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(
        nfeatures=n_features
    )

    kp, des = orb.detectAndCompute(
        gray,
        None
    )

    return kp, des


def match_features(des1, des2, ratio=0.75):
    """
    Brute-Force KNN matching (k=2)
    + Lowe's ratio test.
    """

    bf = cv2.BFMatcher(
        cv2.NORM_HAMMING,
        crossCheck=False
    )

    knn_matches = bf.knnMatch(
        des1,
        des2,
        k=2
    )

    good_matches = []

    for pair in knn_matches:

        if len(pair) == 2:

            m, n = pair

            if m.distance < ratio * n.distance:
                good_matches.append(m)

    good_matches = sorted(
        good_matches,
        key=lambda m: m.distance
    )

    return good_matches


def process_pair(path1, path2, pair_number):
    """
    Compare two images using ORB feature matching
    and save the comparison results separately.
    """

    img1, img2 = load_pair(path1, path2)

    # Detect ORB features
    kp1, des1 = orb_detect(img1)
    kp2, des2 = orb_detect(img2)

    image1_name = os.path.basename(path1)
    image2_name = os.path.basename(path2)

    print(
        f"\n========== Pair {pair_number:02d} =========="
    )

    print(
        f"Image 1: {image1_name}"
    )

    print(
        f"Image 2: {image2_name}"
    )

    print(
        f"Keypoints in image 1: {len(kp1)}"
    )

    print(
        f"Keypoints in image 2: {len(kp2)}"
    )

    # Check descriptors
    if des1 is None or des2 is None:

        print(
            "No descriptors found in one "
            "of the images - cannot compare."
        )

        return

    # --------------------------------------------------
    # FEATURE MATCHING
    # --------------------------------------------------

    good_matches = match_features(
        des1,
        des2,
        ratio=0.75
    )

    total_features = min(
        len(kp1),
        len(kp2)
    )

    if total_features > 0:

        similarity = (
            len(good_matches)
            / total_features
        ) * 100

    else:

        similarity = 0

    # --------------------------------------------------
    # CLASSIFY MATCH
    # --------------------------------------------------

    if len(good_matches) >= 100:

        result = "Strong match"

    elif len(good_matches) >= 50:

        result = "Moderate match"

    elif len(good_matches) >= 20:

        result = "Weak match"

    else:

        result = "Poor match"

    # --------------------------------------------------
    # PRINT COMPARISON
    # --------------------------------------------------

    print("\n----- Comparison -----")

    print(
        f"Total keypoints considered: "
        f"{total_features}"
    )

    print(
        f"Good feature matches: "
        f"{len(good_matches)}"
    )

    print(
        f"Feature similarity: "
        f"{similarity:.2f}%"
    )

    print(
        f"Comparison result: "
        f"{result}"
    )

    # --------------------------------------------------
    # SAVE COMPARISON TO TEXT FILE
    # --------------------------------------------------

    comparison_file = os.path.join(
        COMPARISON_DIR,
        f"pair{pair_number:02d}_comparison.txt"
    )

    with open(
        comparison_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            f"Feature Matching Comparison - "
            f"Pair {pair_number:02d}\n"
        )

        file.write(
            "=" * 50
            + "\n\n"
        )

        file.write(
            f"Image 1: {image1_name}\n"
        )

        file.write(
            f"Image 2: {image2_name}\n\n"
        )

        file.write(
            f"Keypoints in image 1: "
            f"{len(kp1)}\n"
        )

        file.write(
            f"Keypoints in image 2: "
            f"{len(kp2)}\n"
        )

        file.write(
            f"Total keypoints considered: "
            f"{total_features}\n\n"
        )

        file.write(
            f"Good feature matches: "
            f"{len(good_matches)}\n"
        )

        file.write(
            f"Feature similarity: "
            f"{similarity:.2f}%\n"
        )

        file.write(
            f"Comparison result: "
            f"{result}\n"
        )

        file.write(
            "\n"
            + "=" * 50
            + "\n"
        )

        file.write(
            "Matching method: ORB\n"
        )

        file.write(
            "Matcher: Brute-Force Hamming\n"
        )

        file.write(
            "Filtering: Lowe's Ratio Test\n"
        )

    print(
        f"Saved comparison: {comparison_file}"
    )

    # --------------------------------------------------
    # DRAW FEATURE MATCHES
    # --------------------------------------------------

    matched_img = cv2.drawMatches(
        img1,
        kp1,
        img2,
        kp2,
        good_matches[:50],
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )

    # Save visual matching result
    output_path = os.path.join(COMPARISON_DIR,f"{os.path.splitext(os.path.basename(path1))[0]}_vs_{os.path.splitext(os.path.basename(path2))[0]}.jpg")
    cv2.imwrite(output_path, matched_img)

    print( f"Saved matches: {output_path}")


def find_pairs():


    if not os.path.isdir(INPUT_DIR):
        print(f"Folder '{INPUT_DIR}' was not found.")
        return []

    files = sorted(f for f in os.listdir(INPUT_DIR)if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")))

    pairs = []

    # Remove extensions and group files by their
    # common name.
    groups = {}

    for filename in files:

        name, extension = os.path.splitext(filename)

        # Check whether filename ends with 1 or 2
        if name.endswith("1"):

            base_name = name[:-1]

            groups.setdefault(base_name,{})["1"] = filename

        elif name.endswith("2"):

            base_name = name[:-1]

            groups.setdefault(base_name,{})["2"] = filename

    # Create pairs
    for base_name in sorted(groups):

        group = groups[base_name]

        if "1" in group and "2" in group:

            image1 = os.path.join(
                INPUT_DIR,
                group["1"]
            )

            image2 = os.path.join(
                INPUT_DIR,
                group["2"]
            )

            pairs.append(
                (image1, image2)
            )

            print(
                f"Found pair: "
                f"{group['1']} <-> {group['2']}"
            )

        else:

            print(
                f"Incomplete pair: {base_name}"
            )

    return pairs


def main():

    # Manual mode:
    # python feature_matching.py image1.jpg image2.jpg

    if len(sys.argv) == 3:

        os.makedirs(
            OUTPUT_DIR,
            exist_ok=True
        )

        os.makedirs(
            COMPARISON_DIR,
            exist_ok=True
        )

        process_pair(
            sys.argv[1],
            sys.argv[2],
            1
        )

        return

    # Dataset mode

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    os.makedirs(
        COMPARISON_DIR,
        exist_ok=True
    )

    pairs = find_pairs()

    if not pairs:

        print(
            "\nNo valid image pairs found."
        )

        print(
            "\nExpected filenames:"
        )

        print(
            "camera1.jpg"
        )

        print(
            "camera2.jpg"
        )

        return

    print(
        f"\nFound {len(pairs)} image pairs."
    )

    for i, (path1, path2) in enumerate(
        pairs,
        start=1
    ):

        process_pair(
            path1,
            path2,
            i
        )

    print(
        "\n======================================"
    )

    print(
        f"Finished matching {len(pairs)} pairs."
    )

    print(
        f"Match images saved in "
        f"'{OUTPUT_DIR}/'"
    )

    print(
        f"Comparison results saved in "
        f"'{COMPARISON_DIR}/'"
    )

    print(
        "======================================"
    )


if __name__ == "__main__":
    main()
