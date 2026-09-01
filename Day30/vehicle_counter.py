import os
import cv2
from ultralytics import YOLO
from collections import defaultdict


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = "yolov8n.pt"          # pretrained COCO weights (auto-downloads)

# COCO class IDs for vehicles we care about
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

CONF_THRESHOLD = 0.35

# Counting line: horizontal line at LINE_Y (as a fraction of frame height).
# Vehicles are counted when their centroid crosses this line.
LINE_Y_FRACTION = 0.6


def get_line_y(frame_height: int) -> int:
    return int(frame_height * LINE_Y_FRACTION)


def process_video(input_path: str, output_path: str, model: YOLO = None):

    if model is None:
        model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"Could not open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    line_y = get_line_y(height)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # track_history[id] = last known centroid y-coordinate
    track_history = {}
    # counted_ids: prevents the same vehicle being counted more than once
    counted_ids = set()
    # counts per class
    counts = defaultdict(int)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # persist=True keeps track IDs consistent across frames
        results = model.track(
            frame,
            persist=True,
            classes=list(VEHICLE_CLASSES.keys()),
            conf=CONF_THRESHOLD,
            verbose=False,
        )

        # Draw the counting line
        cv2.line(frame, (0, line_y), (width, line_y), (0, 255, 255), 2)

        result = results[0]
        if result.boxes is not None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            track_ids = result.boxes.id.cpu().numpy().astype(int)
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            for box, track_id, cls_id in zip(boxes, track_ids, class_ids):
                x1, y1, x2, y2 = box
                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                class_name = VEHICLE_CLASSES.get(cls_id, "vehicle")

                # --- Line-crossing check ---
                prev_cy = track_history.get(track_id)
                if prev_cy is not None and track_id not in counted_ids:
                    crossed_down = prev_cy < line_y <= cy
                    crossed_up = prev_cy > line_y >= cy
                    if crossed_down or crossed_up:
                        counts[class_name] += 1
                        counted_ids.add(track_id)

                track_history[track_id] = cy

                # --- Draw box + label ---
                color = (100, 255, 40) if track_id in counted_ids else (255, 10, 10)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(frame, f"{class_name} ID:{track_id}", (int(x1), int(y1) - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2,)
                cv2.circle(frame, (cx, cy), 4, color, -1)

        # --- Overlay running counts ---
        y_offset = 30
        total = sum(counts.values())
        cv2.putText(frame, f"Total: {total}", (15, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 163, 25), 2)
        for i, cls_name in enumerate(VEHICLE_CLASSES.values()):
            y_offset += 30
            cv2.putText(frame, f"{cls_name.capitalize()}: {counts[cls_name]}", (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,)

        out.write(frame)

    cap.release()
    out.release()
    return dict(counts)


def reencode_h264(input_path: str, output_path: str):

    os.system(
        f'ffmpeg -y -i "{input_path}" -vcodec libx264 -pix_fmt yuv420p -crf 23 "{output_path}"'
    )


if __name__ == "__main__":
    # Example standalone run
    input_video = os.path.join(SCRIPT_DIR, "input_video", "cars only.mp4")
    raw_output = os.path.join(SCRIPT_DIR, "output_videos", "cars_only_counted_raw.mp4")
    final_output = os.path.join(SCRIPT_DIR, "output_videos", "cars_only_counted.mp4")

    os.makedirs(os.path.dirname(raw_output), exist_ok=True)

    final_counts = process_video(input_video, raw_output)
    reencode_h264(raw_output, final_output)

    print("Final vehicle counts:", final_counts)
