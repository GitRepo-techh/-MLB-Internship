"""
Day 38 - ROI Selector Helper

Click points on a frame from your video to define one or more polygon
Regions of Interest, then this prints out a ready-to-paste ROI_DEFINITIONS
dict (in fraction coordinates) for security_monitor.py.

Controls:
    Left click   - add a point to the current region
    n            - finish current region, type a name for it, start a new one
    z            - undo last point
    s            - save & print ROI_DEFINITIONS, then quit
    q            - quit without saving

Run:
    uv run select_roi.py --input vtest_people.mp4
    uv run select_roi.py --input vtest_people.mp4 --frame 30   # pick a later frame
"""

import argparse
import cv2

# distinct colors cycled through for each region you draw
COLORS = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (0, 200, 200), (255, 0, 255)]


def main():
    parser = argparse.ArgumentParser(description="Pick ROI polygons on a video frame")
    parser.add_argument("--input", required=True, help="Path to video")
    parser.add_argument("--frame", type=int, default=0, help="Frame number to use (default: first frame)")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {args.input}")

    cap.set(cv2.CAP_PROP_POS_FRAMES, args.frame)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not read frame {args.frame} from {args.input}")

    height, width = frame.shape[:2]
    regions = []          # finished regions: list of (name, [(x, y), ...])
    current_points = []   # points for the region being drawn right now

    window = "Click corners | n=next region  z=undo  s=save  q=quit"
    cv2.namedWindow(window)

    def on_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            current_points.append((x, y))

    cv2.setMouseCallback(window, on_click)

    def redraw():
        vis = frame.copy()
        for i, (name, pts) in enumerate(regions):
            color = COLORS[i % len(COLORS)]
            cv2.polylines(vis, [_np_pts(pts)], True, color, 2)
            cv2.putText(vis, name, pts[0], cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        if current_points:
            color = COLORS[len(regions) % len(COLORS)]
            for pt in current_points:
                cv2.circle(vis, pt, 4, color, -1)
            if len(current_points) > 1:
                cv2.polylines(vis, [_np_pts(current_points)], False, color, 2)
        return vis

    def _np_pts(pts):
        import numpy as np
        return np.array(pts, dtype="int32")

    print("Click at least 3 points to outline a region, then press 'n' to name and close it.")

    while True:
        cv2.imshow(window, redraw())
        key = cv2.waitKey(20) & 0xFF

        if key == ord("z") and current_points:
            current_points.pop()

        elif key == ord("n"):
            if len(current_points) < 3:
                print("Need at least 3 points before starting a new region.")
                continue
            name = input("Name this region (e.g. Entrance Zone, Exit Zone): ").strip() or f"Region {len(regions)+1}"
            regions.append((name, current_points.copy()))
            current_points.clear()
            print(f"Saved '{name}' with {len(regions[-1][1])} points.")

        elif key == ord("s"):
            if len(current_points) >= 3:
                name = input("Name this final region: ").strip() or f"Region {len(regions)+1}"
                regions.append((name, current_points.copy()))
                current_points.clear()
            break

        elif key == ord("q"):
            regions = []
            break

    cv2.destroyAllWindows()

    if not regions:
        print("No regions saved.")
        return

    print("\nPaste this into security_monitor.py, replacing ROI_DEFINITIONS:\n")
    print("ROI_DEFINITIONS = {")
    for name, pts in regions:
        frac_pts = [(round(x / width, 3), round(y / height, 3)) for x, y in pts]
        print(f'    "{name}": {frac_pts},')
    print("}")


if __name__ == "__main__":
    main()
