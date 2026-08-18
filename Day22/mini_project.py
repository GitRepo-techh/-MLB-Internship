import cv2
import easyocr
import os
import sys
from datetime import datetime

CONFIDENCE_THRESHOLD = 0.75
output_texts = 'saved_texts/'
os.makedirs(output_texts, exist_ok=True)


def extract_text_from_image(image_path):
    if not os.path.exists(image_path):
        print(f"Error: file not found at {image_path}")
        return

    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: could not read image at {image_path}")
        return

    print("Loading EasyOCR reader...")
    reader = easyocr.Reader(['en'])

    print("Extracting text...")
    results = reader.readtext(image_path)

    extracted_lines = []

    for bbox, text, confidence in results:
        if confidence < CONFIDENCE_THRESHOLD:
            continue

        extracted_lines.append(text)

        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))

        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image, text, (top_left[0], max(top_left[1] - 10, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    full_text = '\n'.join(extracted_lines) if extracted_lines else "No text detected above confidence threshold."

    # Display extracted text in the console
    print("\n----- Extracted Text -----")
    print(full_text)
    print("---------------------------\n")

    # Save extracted text to a .txt file
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    text_path = os.path.join(output_texts, f"{base_name}_{timestamp}.txt")

    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    print(f"Text saved to: {text_path}")

    # Show both original and annotated image
    original = cv2.imread(image_path)
    cv2.imshow("Original Image", original)
    cv2.imshow("Detected Text (Annotated)", image)
    print("Press any key on an image window to close.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("Enter the path to the image: ").strip()

    extract_text_from_image(image_path)