import cv2
import numpy as np
import os


class ShapeDetectionSystem:

    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.valid_extensions = (".jpg", ".jpeg", ".png")
        self.min_area = 150  # filters out noise specks

        os.makedirs(self.output_folder, exist_ok=True)

    # ---------- Core steps ----------

    def load_image(self, filename):
        path = os.path.join(self.input_folder, filename)
        return cv2.imread(path, 1)

    def apply_threshold(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        corners = [
            gray[0, 0], gray[0, w - 1],
            gray[h - 1, 0], gray[h - 1, w - 1]
        ]
        background_is_light = np.mean(corners) > 127

        if background_is_light:
            # Light background, dark outline/fill -> standard grayscale,
            # inverted so the dark shape becomes the white foreground
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, binary = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)
        else:
            # Dark/black background, bright colored fill -> luminance-weighted
            # grayscale under-detects blue/red, so use max across B,G,R instead
            b, g, r = cv2.split(image)
            max_channel = cv2.max(cv2.max(b, g), r)
            blurred = cv2.GaussianBlur(max_channel, (5, 5), 0)
            _, binary = cv2.threshold(blurred, 25, 255, cv2.THRESH_BINARY)

        return binary

    def find_contours(self, binary_image):
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [c for c in contours if cv2.contourArea(c) >= self.min_area]

    # ---------- Classification ----------

    def classify_shape(self, contour):
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        vertices = len(approx)

        area = cv2.contourArea(contour)
        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0

        if circularity > 0.85 and vertices > 6:
            return "Circle"

        shape_names = {
            3: "Triangle",
            5: "Pentagon",
            6: "Hexagon",
            7: "Heptagon",
            8: "Octagon",
            9: "Nonagon",
        }

        if vertices == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            return "Square" if 0.90 <= aspect_ratio <= 1.10 else "Rectangle"
        elif vertices in shape_names:
            return shape_names[vertices]
        elif circularity > 0.8:
            return "Circle"
        else:
            return "Polygon"

    # ---------- Per-image processing ----------

    def process_image(self, filename):
        image = self.load_image(filename)
        if image is None:
            print(f"Skipping {filename} — failed to load.")
            return

        name = os.path.splitext(filename)[0]

        binary = self.apply_threshold(image)
        contours = self.find_contours(binary)

        contour_image = image.copy()
        final_image = image.copy()

        cv2.drawContours(contour_image, contours, -1, (45, 67, 230), 2)

        if not contours:
            print(f"[{filename}] No shapes detected.")

        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            x, y, w, h = cv2.boundingRect(contour)

            shape = self.classify_shape(contour)

            cv2.drawContours(final_image, [contour], -1, (45, 67, 230), 2)
            cv2.rectangle(final_image, (x, y), (x + w, y + h), (255, 0, 0), 2)

            label = f"{shape}"
            metrics = f"A:{area:.0f} P:{perimeter:.0f}"
            cv2.putText(final_image, label, (x, max(y - 25, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 100, 255), 2)
            cv2.putText(final_image, metrics, (x, max(y - 8, 30)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

            print(f"[{filename}] {shape}: area={area:.1f}, perimeter={perimeter:.1f}")

        
        self.save_output(final_image, f"{name}_final.jpg")

    def save_output(self, image, filename):
        save_path = os.path.join(self.output_folder, filename)
        cv2.imwrite(save_path, image)
        print(f"Saved: {save_path}")

    def process_all(self):
        files = sorted(f for f in os.listdir(self.input_folder)
                        if f.lower().endswith(self.valid_extensions))

        print(f"Found {len(files)} images to process.\n")
        for filename in files:
            self.process_image(filename)
        print(f"\nDone. Processed {len(files)} images.")


if __name__ == "__main__":
    system = ShapeDetectionSystem("Input images", "Output images")
    system.process_all()