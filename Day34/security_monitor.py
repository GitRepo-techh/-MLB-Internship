import os
import csv
import argparse
import subprocess
from datetime import datetime, timedelta

import cv2
import numpy as np
from ultralytics import YOLO
import imageio_ffmpeg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = "yolov8n.pt"
PERSON_CLASS_ID = 0
CONF_THRESHOLD = 0.35

# Bundled static ffmpeg binary — no system install / PATH setup needed.
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# --- Define your Regions of Interest here -----------------------------
# Each ROI is a name + a polygon of (x_fraction, y_fraction) points,
# expressed as fractions of the frame width/height so it works on any
# input resolution. Add as many regions as you like.
ROI_DEFINITIONS = {
    "Entrance Zone": [(0.678, 0.431), (0.678, 0.622), (0.913, 0.622), (0.913, 0.431), (0.678, 0.431), (0.678, 0.431)],
    "exit zone": [(0.263, 0.354), (0.263, 0.467), (0.483, 0.465), (0.483, 0.354), (0.263, 0.354)],
}

ROI_COLORS = {
    "Entrance Zone": (0, 250, 0),
    "Restricted Area": (0, 0, 255),
}


def reencode_h264(raw_path: str, final_path: str) -> None:
    cmd = [FFMPEG_EXE, "-y", "-i", raw_path, "-vcodec", "libx264", "-pix_fmt", "yuv420p", final_path]
    subprocess.run(cmd, check=True, capture_output=True)
    os.remove(raw_path)


def polygon_points(roi_fracs, width, height):
    return [(int(x * width), int(y * height)) for x, y in roi_fracs]


def point_in_polygon(cx, cy, polygon):
    return cv2.pointPolygonTest(np.array(polygon, dtype="int32"), (cx, cy), False) >= 0


def run_security_monitor(input_path: str, output_video: str, output_csv: str) -> dict:
    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    raw_path = output_video.replace(".mp4", "_raw.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(raw_path, fourcc, fps, (width, height))

    # Precompute pixel polygons for each ROI
    roi_polygons = {name: polygon_points(pts, width, height) for name, pts in ROI_DEFINITIONS.items()}

    # state[region][track_id] = entry_frame_idx (None if not currently inside)
    state = {name: {} for name in ROI_DEFINITIONS}
    events = []  # rows to write to CSV
    base_time = datetime.now()

    frame_idx = 0

    results_stream = model.track(
        source=input_path,
        classes=[PERSON_CLASS_ID],
        conf=CONF_THRESHOLD,
        persist=True,
        tracker="bytetrack.yaml",
        stream=True,
        verbose=False,
    )

    def frame_time(idx):
        return base_time + timedelta(seconds=idx / fps)

    for result in results_stream:
        frame = result.orig_img.copy()
        frame_idx += 1

        # draw ROI outlines
        for name, poly in roi_polygons.items():
            color = ROI_COLORS.get(name, (0, 200, 200))
            cv2.polylines(frame, [np.array(poly, dtype="int32")], True, color, 2)
            cv2.putText(frame, name, poly[0], cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        boxes = result.boxes
        present_ids_by_region = {name: set() for name in ROI_DEFINITIONS}

        if boxes is not None and boxes.id is not None:
            xyxy = boxes.xyxy.cpu().numpy()
            ids = boxes.id.cpu().numpy().astype(int)

            for (x1, y1, x2, y2), tid in zip(xyxy, ids):
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
                cv2.putText(frame, f"ID {tid}", (x1, max(y1 - 8, 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 2)

                for name, poly in roi_polygons.items():
                    if point_in_polygon(cx, cy, poly):
                        present_ids_by_region[name].add(tid)

        # --- diff against previous frame's state to fire enter/exit events ---
        for name in ROI_DEFINITIONS:
            currently_inside = present_ids_by_region[name]
            tracked_inside = state[name]

            # New entries
            for tid in currently_inside - tracked_inside.keys():
                tracked_inside[tid] = frame_idx

            # Exits
            for tid in list(tracked_inside.keys() - currently_inside):
                entry_frame = tracked_inside.pop(tid)
                entry_t = frame_time(entry_frame)
                exit_t = frame_time(frame_idx)
                duration = (exit_t - entry_t).total_seconds()
                events.append([
                    tid, name,
                    entry_t.strftime("%Y-%m-%d %H:%M:%S"),
                    exit_t.strftime("%Y-%m-%d %H:%M:%S"),
                    round(duration, 2),
                ])

        # overlay active counts per region
        y_off = 30
        cv2.rectangle(frame, (0, 0), (300, 25 + 25 * len(ROI_DEFINITIONS)), (0, 0, 0), -1)
        for name in ROI_DEFINITIONS:
            cv2.putText(frame, f"{name}: {len(state[name])} active", (10, y_off),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
            y_off += 25

        writer.write(frame)

    # Anyone still inside a region when the video ends counts as an exit
    # at the final frame, so their event is captured too.
    for name in ROI_DEFINITIONS:
        for tid, entry_frame in state[name].items():
            entry_t = frame_time(entry_frame)
            exit_t = frame_time(frame_idx)
            duration = (exit_t - entry_t).total_seconds()
            events.append([
                tid, name,
                entry_t.strftime("%Y-%m-%d %H:%M:%S"),
                exit_t.strftime("%Y-%m-%d %H:%M:%S"),
                round(duration, 2),
            ])

    writer.release()
    reencode_h264(raw_path, output_video)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, "w", newline="") as f:
        writer_csv = csv.writer(f)
        writer_csv.writerow(["track_id", "region", "entry_time", "exit_time", "duration_seconds"])
        writer_csv.writerows(sorted(events, key=lambda r: r[2]))

    print(f"Frames processed : {frame_idx}")
    print(f"Events logged    : {len(events)}")
    print(f"Video saved to   : {output_video}")
    print(f"CSV log saved to : {output_csv}")

    return {"frames": frame_idx, "events": len(events), "video": output_video, "csv": output_csv}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Day 38 security monitoring with ROI event logging")
    parser.add_argument("--input", required=True, help="Path to input video")
    parser.add_argument("--output-video", default=None, help="Path to save annotated output video")
    parser.add_argument("--output-csv", default=None, help="Path to save event log CSV")
    args = parser.parse_args()

    stem = os.path.splitext(os.path.basename(args.input))[0]
    out_video = args.output_video or os.path.join(BASE_DIR, "output_videos", f"{stem}_monitored.mp4")
    out_csv = args.output_csv or os.path.join(BASE_DIR, "event_logs", f"{stem}_events.csv")

    os.makedirs(os.path.dirname(out_video), exist_ok=True)
    run_security_monitor(args.input, out_video, out_csv)
