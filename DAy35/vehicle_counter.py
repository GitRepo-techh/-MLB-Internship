import os
import csv
from collections import defaultdict

import cv2
from ultralytics import YOLO

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# COCO class IDs we care about
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

# Distinct BGR color per class for cleaner visualization
CLASS_COLORS = {
    "car": (60, 200, 255),
    "motorcycle": (255, 120, 60),
    "bus": (120, 60, 255),
    "truck": (60, 255, 120),
}

# Tracker choices exposed in the UI.
# BoT-SORT with a longer track buffer survives brief occlusion (e.g. two
# vehicles crossing paths) far better than default ByteTrack, which is why
# it's the recommended option for the "consistent ID" requirement.
DEFAULT_TRACKERS = {
    "ByteTrack (fast)": "bytetrack.yaml",
    "BoT-SORT (stable IDs)": os.path.join(SCRIPT_DIR, "trackers", "botsort_stable.yaml"),
}


class VehicleCounter:


    def __init__(self, model_path="yolov8n.pt", conf=0.35, iou=0.5,
                 tracker="bytetrack.yaml", trail_len=15):
        self.model = YOLO(model_path)
        self.conf = conf
        self.iou = iou
        self.tracker = tracker
        self.trail_len = trail_len
        self.reset_tracking_state()

    def reset_tracking_state(self):

        self.prev_side = {}            # track_id -> last side-of-line sign (-1/0/1)
        self.counted_ids = set()       # track_ids already counted (no double-counting)
        self.counts = defaultdict(int)  # class_name -> running total
        self.trails = defaultdict(list)  # track_id -> recent centroid points
        self.crossing_log = []         # rows for the CSV report

    @staticmethod
    def _side(px, py, x1, y1, x2, y2):

 
        val = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
        if val > 0:
            return 1
        if val < 0:
            return -1
        return 0

    def process_frame(self, frame, frame_idx, fps, line):

        lx1, ly1, lx2, ly2 = line

        try:
            results = self.model.track(
                frame,
                persist=True,
                classes=list(VEHICLE_CLASSES.keys()),
                conf=self.conf,
                iou=self.iou,
                tracker=self.tracker,
                verbose=False,
            )
        except Exception as e:
            # Don't let one bad frame kill an entire video run
            cv2.putText(frame, f"Tracking error: {e}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            return frame

        result = results[0]

        if result.boxes is not None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            track_ids = result.boxes.id.cpu().numpy().astype(int)
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            for box, track_id, cls_id in zip(boxes, track_ids, class_ids):
                bx1, by1, bx2, by2 = box
                cx, cy = int((bx1 + bx2) / 2), int((by1 + by2) / 2)
                class_name = VEHICLE_CLASSES.get(cls_id, "vehicle")
                color = CLASS_COLORS.get(class_name, (200, 200, 200))

                side = self._side(cx, cy, lx1, ly1, lx2, ly2)
                prev = self.prev_side.get(track_id)
                if (prev is not None and prev != 0 and side != 0
                        and side != prev and track_id not in self.counted_ids):
                    self.counts[class_name] += 1
                    self.counted_ids.add(track_id)
                    self.crossing_log.append({
                        "track_id": int(track_id),
                        "class": class_name,
                        "frame": frame_idx,
                        "timestamp_sec": round(frame_idx / fps, 2) if fps else 0,
                        "direction": "forward" if side > prev else "backward",
                    })
                self.prev_side[track_id] = side

                # Motion trail (visual proof that an ID stayed consistent
                # through a crossing, instead of jumping between vehicles)
                trail = self.trails[track_id]
                trail.append((cx, cy))
                if len(trail) > self.trail_len:
                    trail.pop(0)

                box_color = (80, 220, 80) if track_id in self.counted_ids else color
                cv2.rectangle(frame, (int(bx1), int(by1)), (int(bx2), int(by2)), box_color, 2)
                cv2.putText(frame, f"{class_name} #{track_id}", (int(bx1), max(15, int(by1) - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)
                for i in range(1, len(trail)):
                    cv2.line(frame, trail[i - 1], trail[i], box_color, 2)
                cv2.circle(frame, (cx, cy), 3, box_color, -1)

        # Counting line
        cv2.line(frame, (lx1, ly1), (lx2, ly2), (0, 230, 255), 3)

        # Semi-transparent stats panel (cleaner than raw text-on-video)
        panel_h = 34 + 26 * len(VEHICLE_CLASSES)
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (230, panel_h), (20, 20, 20), -1)
        frame[:] = cv2.addWeighted(overlay, 0.55, frame, 0.45, 0)

        total = sum(self.counts.values())
        cv2.putText(frame, f"Total: {total}", (20, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 120), 2)
        y = 58
        for cls_name in VEHICLE_CLASSES.values():
            cv2.putText(frame, f"{cls_name}: {self.counts[cls_name]}", (20, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            y += 26

        return frame

    def process_video(self, input_path, output_path, line=None, progress_cb=None):

      
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise IOError(f"Could not open video: {input_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0

        if width == 0 or height == 0:
            cap.release()
            raise IOError("Video reported zero width/height - file may be corrupt.")

        if line is None:
            line = (0, int(height * 0.6), width, int(height * 0.6))

        self.reset_tracking_state()

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if not out.isOpened():
            cap.release()
            raise IOError(f"Could not open VideoWriter for: {output_path}")

        frame_idx = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = self.process_frame(frame, frame_idx, fps, line)
                out.write(frame)
                frame_idx += 1
                if progress_cb and total_frames:
                    progress_cb(min(frame_idx / total_frames, 1.0))
        finally:
            cap.release()
            out.release()

        if frame_idx == 0:
            raise IOError("No frames could be read from the video.")

        return dict(self.counts), list(self.crossing_log)

    def process_image(self, input_path, output_path):

  
        frame = cv2.imread(input_path)
        if frame is None:
            raise IOError(f"Could not read image: {input_path}")

        results = self.model.predict(
            frame, classes=list(VEHICLE_CLASSES.keys()),
            conf=self.conf, iou=self.iou, verbose=False,
        )
        result = results[0]
        counts = defaultdict(int)

        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)
            for box, cls_id in zip(boxes, class_ids):
                x1, y1, x2, y2 = box
                class_name = VEHICLE_CLASSES.get(cls_id, "vehicle")
                counts[class_name] += 1
                color = CLASS_COLORS.get(class_name, (200, 200, 200))
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(frame, class_name, (int(x1), max(15, int(y1) - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        if not cv2.imwrite(output_path, frame):
            raise IOError(f"Could not write output image: {output_path}")

        return dict(counts)


def reencode_h264(input_path, output_path):
    """OpenCV's mp4v output isn't browser-playable - re-encode to H.264 for Streamlit."""
    ret = os.system(f'ffmpeg -y -i "{input_path}" -vcodec libx264 -pix_fmt yuv420p -crf 23 "{output_path}"')
    if ret != 0 or not os.path.exists(output_path):
        raise RuntimeError("ffmpeg re-encoding failed - is ffmpeg installed / on PATH?")


def write_csv(crossing_log, csv_path):
    fieldnames = ["track_id", "class", "frame", "timestamp_sec", "direction"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in crossing_log:
            writer.writerow(row)


if __name__ == "__main__":
    # Headless example run, same shape as the original Day-31 script
    input_video = os.path.join(SCRIPT_DIR, "input_video", "video 1.mp4")
    raw_output = os.path.join(SCRIPT_DIR, "sample_output", "counted_raw.mp4")
    final_output = os.path.join(SCRIPT_DIR, "sample_output", "counted.mp4")
    csv_output = os.path.join(SCRIPT_DIR, "sample_output", "crossings.csv")

    os.makedirs(os.path.dirname(raw_output), exist_ok=True)

    counter = VehicleCounter(conf=0.35, iou=0.5, tracker=DEFAULT_TRACKERS["BoT-SORT (stable IDs)"])
    counts, log = counter.process_video(
        input_video, raw_output,
        progress_cb=lambda p: print(f"\rProcessing: {p:.0%}", end=""),
    )
    print()
    reencode_h264(raw_output, final_output)
    write_csv(log, csv_output)
    print("Final counts:", counts)
    print(f"Saved: {final_output}, {csv_output}")
