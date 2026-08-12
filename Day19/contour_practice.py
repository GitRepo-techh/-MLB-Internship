import os
import cv2 
import numpy as np 


# Complete the following tasks:
# Read an image and convert it to grayscale.
# Apply thresholding.
# Detect contours.
# Draw all contours on the image.
# Calculate the area and perimeter of each contour.
# Draw a bounding rectangle around each detected object.
# Detect simple shapes such as circles, rectangles, squares, and triangles.
# Save all output images.




input_path = "Input images/Rectangle.jpeg"
output_folder = "Output images"
os.makedirs(output_folder, exist_ok=True)

image = cv2.imread(input_path, 1)
if image is None:
    raise FileNotFoundError(f"Could not load {input_path}")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (7, 7), 0)
ret, binary = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)


contours, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

contour_image = image.copy()
cv2.drawContours(contour_image, contours, -1, (45, 67, 230), 2)


def classify_shape(contour):
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
    vertices = len(approx)

    if vertices == 3:
        return "Triangle"
    elif vertices == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = w / float(h)
        return "Square" if 0.90 <= aspect_ratio <= 1.10 else "Rectangle"
    else:
        area = cv2.contourArea(contour)
        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
        return "Circle" if circularity > 0.8 else "Polygon"


final_image = image.copy()
min_area = 100  # filter out noise specks

for contour in contours:
    area = cv2.contourArea(contour)
    if area < min_area:
        continue  # skip noise

    perimeter = cv2.arcLength(contour, True)

    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(final_image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    (cx, cy), radius = cv2.minEnclosingCircle(contour)
    cv2.circle(final_image, (int(cx), int(cy)), int(radius), (0, 0, 255), 1)

    shape = classify_shape(contour)
    cv2.drawContours(final_image, [contour], -1, (45, 67, 230), 2)
    cv2.putText(final_image, shape, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    print(f"{shape}: area={area:.1f}, perimeter={perimeter:.1f}")

# ---------- Save outputs ----------
cv2.imwrite(os.path.join(output_folder, "gray.jpg"), gray)
cv2.imwrite(os.path.join(output_folder, "binary.jpg"), binary)
cv2.imwrite(os.path.join(output_folder, "contours.jpg"), contour_image)
cv2.imwrite(os.path.join(output_folder, "final_shapes.jpg"), final_image)

# ---------- Display ----------
gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
blur_bgr = cv2.cvtColor(blur, cv2.COLOR_GRAY2BGR)
binary_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

combined = np.hstack((gray_bgr, blur_bgr, binary_bgr, contour_image))
cv2.imshow("GrayScale | Blur | Binary | Contours", combined)
cv2.imshow("Final Shape Detection", final_image)

cv2.waitKey(0)
cv2.destroyAllWindows()








