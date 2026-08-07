import cv2
import numpy as np




def load_image(path):


    image = cv2.imread(path, 1)  
    print(f"Loaded image. Shape: {image.shape}, Size: {image.size}")
    return image


def to_grayscale(image):


    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # convert back to 3-channel so it still displays/saves like a normal image
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def resize_image(image):


    print("1. Resize by exact width/height")
    print("2. Resize by scale factor")
    choice = input("Choose an option: ").strip()

    if choice == "1":
        width = int(input("Enter new width: "))
        height = int(input("Enter new height: "))
        return cv2.resize(image, (width, height))
    elif choice == "2":
        fx = float(input("Enter scale factor for width (e.g. 0.5): "))
        fy = float(input("Enter scale factor for height (e.g. 0.5): "))
        return cv2.resize(image, (0, 0), fx=fx, fy=fy)
    else:
        print("Invalid choice, returning original image.")
        return image


def rotate_image(image):


    print("1. Rotate 90 clockwise")
    print("2. Rotate 90 counter-clockwise")
    print("3. Rotate 180")
    print("4. Rotate by custom angle")
    choice = input("Choose an option: ").strip()

    if choice == "1":
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif choice == "2":
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif choice == "3":
        return cv2.rotate(image, cv2.ROTATE_180)
    elif choice == "4":
        angle = float(input("Enter angle in degrees: "))
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, matrix, (w, h))
    else:
        print("Invalid choice, returning original image.")
        return image


def flip_image(image):


    print("1. Flip horizontal")
    print("2. Flip vertical")
    print("3. Flip both")
    choice = input("Choose an option: ").strip()

    flip_codes = {"1": 1, "2": 0, "3": -1}
    if choice in flip_codes:
        return cv2.flip(image, flip_codes[choice])
    else:
        print("Invalid choice, returning original image.")
        return image


def crop_image(image):


    h, w = image.shape[:2]
    print(f"Image size is width={w}, height={h}")
    x1 = int(input("Enter x1: "))
    y1 = int(input("Enter y1: "))
    x2 = int(input("Enter x2: "))
    y2 = int(input("Enter y2: "))

    # clamp values so bad input doesn't crash the program
    x1, x2 = sorted((max(0, min(x1, w)), max(0, min(x2, w))))
    y1, y2 = sorted((max(0, min(y1, h)), max(0, min(y2, h))))
    return image[y1:y2, x1:x2]


def get_color(prompt="Enter color as B,G,R (e.g. 255,0,0): "):


    raw = input(prompt).strip()
    try:
        b, g, r = (int(v) for v in raw.split(","))
        return (b, g, r)
    except ValueError:
        print("Invalid format, defaulting to red (0,0,255).")
        return (0, 0, 255)


def draw_shapes(image):


    print("1. Rectangle")
    print("2. Line")
    print("3. Circle")
    print("4. Polygon")
    choice = input("Choose a shape: ").strip()
    color = get_color()
    thickness = int(input("Enter thickness (use -1 to fill): "))

    output = image.copy()

    if choice == "1":
        x1, y1 = map(int, input("Enter top-left point x,y: ").split(","))
        x2, y2 = map(int, input("Enter bottom-right point x,y: ").split(","))
        cv2.rectangle(output, (x1, y1), (x2, y2), color, thickness)

    elif choice == "2":
        x1, y1 = map(int, input("Enter start point x,y: ").split(","))
        x2, y2 = map(int, input("Enter end point x,y: ").split(","))
        cv2.line(output, (x1, y1), (x2, y2), color, thickness)

    elif choice == "3":
        cx, cy = map(int, input("Enter center point x,y: ").split(","))
        radius = int(input("Enter radius: "))
        cv2.circle(output, (cx, cy), radius, color, thickness)

    elif choice == "4":
        n = int(input("How many points? "))
        points = []
        for i in range(n):
            x, y = map(int, input(f"Point {i + 1} x,y: ").split(","))
            points.append([x, y])
        pts = np.array(points, np.int32).reshape((-1, 1, 2))
        cv2.polylines(output, [pts], True, color, thickness)

    else:
        print("Invalid choice, returning original image.")
        return image

    return output


def add_text(image):


    text = input("Enter text to add: ")
    x, y = map(int, input("Enter position x,y: ").split(","))
    color = get_color()
    font_scale = float(input("Enter font scale (e.g. 1): "))
    thickness = int(input("Enter thickness (e.g. 2): "))

    output = image.copy()
    cv2.putText(output, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, color, thickness)
    
    return output


def save_image(image):


    path = input("Enter filename to save as (e.g. output.png): ").strip()

    cv2.imwrite(path, image)
    print(f"Saved to '{path}'.")


# Bonus Features:

def adjust_brightness_contrast(image):


    brightness = int(input("Enter brightness value (-100 to 100, 0 = no change): "))
    contrast = float(input("Enter contrast value (e.g. 1.0 = no change, 1.5 = more contrast): "))

    return cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)


def compare_bgr_rgb(image):



    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    combined = np.hstack((image, rgb_image))

    cv2.imshow("BGR (left)  vs  RGB (right)", combined)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_side_by_side(original, processed):

 
    if original.shape != processed.shape:
        processed_resized = cv2.resize(processed, (original.shape[1], original.shape[0]))
    else:
        processed_resized = processed

    combined = np.hstack((original, processed_resized))

    cv2.imshow("Original (left)  vs  Processed (right)", combined)

    cv2.waitKey(0)
    cv2.destroyAllWindows()




MENU = """
========== IMAGE PROCESSING TOOLKIT ==========

1.  Load an image
2.  Convert to grayscale
3.  Resize image
4.  Rotate image
5.  Flip image
6.  Crop image
7.  Draw shapes
8.  Add custom text
9.  Save processed image
10. Show current image
--- Bonus ---
11. Adjust brightness/contrast
12. Compare BGR vs RGB
13. Show original vs processed side by side
0.  Exit

"""


def main():
    original = None
    image = None

    while True:
        print(MENU)
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            path = input("Enter image path: ").strip()
            loaded = load_image(path)
            if loaded is not None:
                original = loaded.copy()
                image = loaded.copy()

        elif image is None:
            print("Please load an image first (option 1).")
            continue

        elif choice == "2":
            image = to_grayscale(image)

        elif choice == "3":
            image = resize_image(image)

        elif choice == "4":
            image = rotate_image(image)

        elif choice == "5":
            image = flip_image(image)

        elif choice == "6":
            image = crop_image(image)

        elif choice == "7":
            image = draw_shapes(image)

        elif choice == "8":
            image = add_text(image)

        elif choice == "9":
            save_image(image)

        elif choice == "10":
            cv2.imshow("Current Image", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        elif choice == "11":
            image = adjust_brightness_contrast(image)

        elif choice == "12":
            compare_bgr_rgb(image)

        elif choice == "13":
            show_side_by_side(original, image)

        elif choice == "0":
            print("Exiting. Goodbye!")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()




