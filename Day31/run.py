import cv2
import json
import os
from parking_detection import ParkingDetector


# ---------------------------------
# 1. Load parking spaces
# ---------------------------------

with open("spaces/parking_spaces.json", "r") as file:
    parking_spaces_data = json.load(file)

# Convert list format to dictionary format
parking_spaces = {
    str(i + 1): polygon
    for i, polygon in enumerate(parking_spaces_data)
}

print(f"Loaded {len(parking_spaces)} parking spaces.")


# ---------------------------------
# 2. Load YOLO detector
# ---------------------------------

detector = ParkingDetector()


# ---------------------------------
# 3. Open parking video
# ---------------------------------

video_path = "input_videos/carPark.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"ERROR: Could not open video: {video_path}")
    exit()


# ---------------------------------
# 4. Get video information
# ---------------------------------

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"Video resolution: {width} x {height}")
print(f"FPS: {fps}")


# ---------------------------------
# 5. Create output folder
# ---------------------------------

output_folder = "output_videos"


# ---------------------------------
# 6. Create output video
# ---------------------------------

output_path = os.path.join(output_folder, "parking_detection.mp4")

fourcc = cv2.VideoWriter_fourcc(
    *"mp4v"
)

out = cv2.VideoWriter(
    output_path,
    fourcc,
    fps,
    (width, height)
)


# ---------------------------------
# 7. Process video frame by frame
# ---------------------------------

while True:

    ret, frame = cap.read()

    if not ret:
        break

    vehicles, occupied_spaces = detector.process_frame(
        frame,
        parking_spaces,
        confidence=0.25
    )

    output = detector.draw_monitor(
        frame,
        parking_spaces,
        occupied_spaces,
        vehicles
    )

    out.write(output)

    cv2.imshow(
        "Parking Detection",
        output
    )

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ---------------------------------
# 8. Cleanup
# ---------------------------------

cap.release()
out.release()
cv2.destroyAllWindows()


print()
print("Parking detection completed.")
print(f"Output saved to: {output_path}")