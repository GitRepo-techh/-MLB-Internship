import cv2
import json
import os

VIDEO = "input_videos/carPark.mp4"
OUTPUT = "spaces/parking_spaces.json"

os.makedirs("spaces", exist_ok=True)

cap = cv2.VideoCapture(VIDEO)

ret, frame = cap.read()
cap.release()

if not ret:
    print("Could not open video.")
    exit()

spaces = []
current_polygon = []

display = frame.copy()


def mouse_callback(event, x, y, flags, param):
    global current_polygon, display

    if event == cv2.EVENT_LBUTTONDOWN:
        current_polygon.append([x, y])

        cv2.circle(display, (x, y), 5, (0, 255, 255), -1)

        if len(current_polygon) > 1:
            cv2.line(
                display,
                tuple(current_polygon[-2]),
                tuple(current_polygon[-1]),
                (0, 255, 255),
                2
            )


cv2.namedWindow("Draw Parking Spaces")
cv2.setMouseCallback("Draw Parking Spaces", mouse_callback)

print("""
DRAW PARKING SPACES

LEFT CLICK  → add polygon point
ENTER       → finish current parking space
R           → reset current polygon
Q           → save and quit
""")

while True:

    display = frame.copy()

    # Draw already saved spaces
    for i, polygon in enumerate(spaces):

        pts = [tuple(point) for point in polygon]

        cv2.polylines(
            display,
            [__import__("numpy").array(pts, dtype="int32")],
            True,
            (0, 255, 0),
            2
        )

        x, y = pts[0]

        cv2.putText(
            display,
            str(i + 1),
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

    # Draw current polygon
    if len(current_polygon) > 0:

        for point in current_polygon:
            cv2.circle(
                display,
                tuple(point),
                5,
                (0, 255, 255),
                -1
            )

        if len(current_polygon) > 1:
            pts = __import__("numpy").array(
                current_polygon,
                dtype="int32"
            )

            cv2.polylines(
                display,
                [pts],
                False,
                (0, 255, 255),
                2
            )

    cv2.imshow("Draw Parking Spaces", display)

    key = cv2.waitKey(1) & 0xFF

    # ENTER → save current polygon
    if key == 13:

        if len(current_polygon) >= 3:

            spaces.append(current_polygon.copy())

            print(
                f"Saved parking space #{len(spaces)}"
            )

            current_polygon = []

        else:
            print("A parking space needs at least 3 points.")

    # R → reset current polygon
    elif key == ord("r"):

        current_polygon = []

        print("Current polygon reset.")

    # Q → save and quit
    elif key == ord("q"):

        break


cv2.destroyAllWindows()

with open(OUTPUT, "w") as f:
    json.dump(spaces, f, indent=4)

print()
print(f"Saved {len(spaces)} parking spaces.")
print(f"File: {OUTPUT}")