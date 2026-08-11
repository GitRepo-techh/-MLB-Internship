import cv2
import numpy as np
import os




# Build a Python application that detects the boundaries of documents using OpenCV.
# Your application should:
# 1. Load a document image.
# 2. Convert it to grayscale.
# 3. Apply Gaussian Blur.
# 4. Detect edges using Canny Edge Detection.
# 5. Apply morphological operations to remove noise.
# 6. The document boundary (largest contour).
# 7. Draw the detected boundary on the original image.
# 8. Save the final output image.

class DocumentScanner:


    def __init__(self, input_folder, output_folder):


        self.input_folder = input_folder
        self.output_folder = output_folder
        self.valid_extensions = (".jpg", ".jpeg", ".png")

        os.makedirs(self.output_folder, exist_ok=True)

    def load_image(self, filename):

        path = os.path.join(self.input_folder, filename)
        image = cv2.imread(path)  # color, since we need it later to draw + save
        return image

    def to_grayscale(self, image):

        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def apply_blur(self, gray_image):

        return cv2.GaussianBlur(gray_image, (15, 15), sigmaX=0)
    
    def remove_text_noise(self, gray_image):

        kernel = np.ones((25, 25), np.uint8)  # large relative to text size
        closed = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)
        return closed

    def detect_edges(self, blurred_image):

        return cv2.Canny(blurred_image, 20, 90)

    def clean_edges(self, edge_image):

        kernel = np.ones((47, 47), np.uint8)  # was (5,5) or (9,9)
        closed = cv2.morphologyEx(edge_image, cv2.MORPH_CLOSE, kernel, iterations=2)
        return closed

    def find_document_contour(self, cleaned_edges):

        contours, _ = cv2.findContours(cleaned_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        image_area = cleaned_edges.shape[0] * cleaned_edges.shape[1]
        min_area = 0.1 * image_area

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                break

            # Solidity check: how "filled in" / convex the shape is.
            # A real document boundary is close to its own convex hull (solidity near 1).
            # A blob of merged text is jagged and has lots of gaps (solidity much lower).

            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0

            if solidity < 0.85:  # tune this threshold
                continue  # skip this contour, it's likely a text blob, not the document

            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            if len(approx) == 4:
                return approx

        return contours[0]  # fallback

    def draw_boundary(self, original_image, contour):

        output = original_image.copy()
        cv2.drawContours(output, [contour], -1, (0, 255, 0), 3)

        return output

    def save_output(self, image, filename):
        
        save_path = os.path.join(self.output_folder, f"boundary_{filename}")
        cv2.imwrite(save_path, image)
        print(f"Saved: {save_path}")

    def process_image(self, filename):

        image = self.load_image(filename)
        if image is None:
            print(f"Skipping {filename} — failed to load.")
            return

        gray = self.to_grayscale(image)
        blurred = self.apply_blur(gray)
        edges = self.detect_edges(blurred)
        cleaned = self.clean_edges(edges)
        contour = self.find_document_contour(cleaned)

        if contour is None:
            print(f"No contour found for {filename}.")
            return

        result = self.draw_boundary(image, contour)
        self.save_output(result, filename)

    def process_all(self):
        for filename in sorted(os.listdir(self.input_folder)):
            if filename.lower().endswith(self.valid_extensions):
                self.process_image(filename)






if __name__ == "__main__":
    scanner = DocumentScanner("Input images", "Output images")
    scanner.process_all()

    # Folder where all results will be stored
    output_folder = "challenge_task_image"
    os.makedirs(output_folder, exist_ok=True)

    # Process every image again for saving the intermediate results
    for filename in sorted(os.listdir("Input images")):

        if filename.lower().endswith((".jpg", ".jpeg", ".png")):

            image = cv2.imread(os.path.join("Input images", filename))



            if image is None:
                continue

            # Resize image to 800 x 600 
            image = cv2.resize(image, (300, 300))

            # Re-run the same processing using your existing methods
            gray = scanner.to_grayscale(image)
            blurred = scanner.apply_blur(gray)
            edges = scanner.detect_edges(blurred)
            cleaned = scanner.clean_edges(edges)
            contour = scanner.find_document_contour(cleaned)

            if contour is None:
                print(f"No contour found for {filename}.")
                continue

            # Final image with detected boundary
            final_image = scanner.draw_boundary(image, contour)

            combined = np.hstack(( image, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR), cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR), final_image))

            cv2.imshow("All Results: ORIGINAL | CANNY | MORPHOLOGICAL_BITS | EDGE DETECTION", combined)

            # Remove extension from filename
            image_name = os.path.splitext(filename)[0]

            # Create folder for each image
            image_folder = os.path.join(output_folder, image_name)
            os.makedirs(image_folder, exist_ok=True)

            # ==========================================
            # IMWRITE - Save all required images
            # ==========================================

            cv2.imwrite(
                os.path.join(image_folder, "Original_Image.jpg"),
                image
            )

            cv2.imwrite(
                os.path.join(image_folder, "Edge_Detection_Result.jpg"),
                edges
            )

            cv2.imwrite(
                os.path.join(image_folder, "Morphological_Operation_Result.jpg"),
                cleaned
            )

            cv2.imwrite(
                os.path.join(image_folder, "Final_Image_with_Detected_Document_Boundary.jpg"),
                final_image
            )


            print(f"Saved all results for: {filename}")

            # Press any key to continue to the next image
            cv2.waitKey(0)

            # Close windows before showing the next image
            cv2.destroyAllWindows()

    print("\nAll images have been saved in the 'challenge_task_image' folder.")






