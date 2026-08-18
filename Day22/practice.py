import cv2
import easyocr
import os

reader = easyocr.Reader(['en'])
input_images = 'input_images/'
output_texts = 'output_texts/'
output_images = 'output_images/'
confidence_thr = 0.70

os.makedirs(output_texts, exist_ok=True)
os.makedirs(output_images, exist_ok=True)

for image_name in os.listdir(input_images):
    image_path = os.path.join(input_images, image_name)
    image = cv2.imread(image_path)

    if image is None:
        print(f"An error occurred loading: {image_name}")
        continue

    results = reader.readtext(image_path)
    extracted_lines = []

    for bbox, text, confidence in results:
        if confidence < confidence_thr:
            continue

        extracted_lines.append(text)

        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))

        cv2.rectangle(image, top_left, bottom_right, (12, 173, 200), 2)
        cv2.putText(image, text, (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (10, 0, 0), 2)

    base_name = os.path.splitext(image_name)[0]

    text_path = os.path.join(output_texts, f"{base_name}.txt")
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(extracted_lines))

    result_image_path = os.path.join(output_images, image_name)
    cv2.imwrite(result_image_path, image)

    print(f"Processed {image_name}: {len(extracted_lines)} lines kept (>= {confidence_thr})")

print("Done. Check output_texts/ and output_images/")