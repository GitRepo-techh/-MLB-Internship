"""
traffic_violation.py
---------------------
Core rule-based violation logic:
  - direction calculation per tracked vehicle (movement vector over its recent history)
  - wrong-way detection (movement direction vs. defined normal direction)
  - restricted-zone detection (point-in-polygon test on vehicle centroid)
  - duplicate-violation suppression (a track ID is only flagged once per violation type)
  - drawing routines for the two demo variants
  - end-to-end process_video() pipeline used by both app.py and test_run.py
"""

import os
import subprocess
from collections import defaultdict, deque

import cv2
import numpy as np


# ---------------------------------------------------------------------------
# Violation detector
# ---------------------------------------------------------------------------

class TrafficViolationDetector:
    def __init__(
        self,
        normal_direction=(0, 1),      # unit vector describing "normal" traffic flow
        direction_threshold=-0.3,     # cosine similarity below this => wrong-way
        min_track_len=5,              # min history points before judging direction
        restricted_zone=None,         # list of (x, y) polygon points in pixel coords
        history_len=30,
    ):
        self.normal_direction = self._normalize(normal_direction)
        self.direction_threshold = direction_threshold
        self.min_track_len = min_track_len
        self.restricted_zone = (
            np.array(restricted_zone, dtype=np.int32) if restricted_zone is not None else None
        )

        self.track_history = defaultdict(lambda: deque(maxlen=history_len))
        self.vehicle_type_by_id = {}

        # duplicate-suppression sets: once a track_id lands here, it is never re-flagged
        self.wrong_way_ids = set()
        self.zone_violation_ids = set()

        self.violation_events = []  # ordered list of {track_id, vehicle_type, violation_type, frame, timestamp_sec}

    @staticmethod
    def _normalize(vec):
        v = np.array(vec, dtype=float)
        n = np.linalg.norm(v)
        return v / n if n > 0 else v

    def _movement_vector(self, track_id):
        pts = self.track_history[track_id]
        if len(pts) < self.min_track_len:
            return None
        start = np.array(pts[0])
        end = np.array(pts[-1])
        vec = end - start
        norm = np.linalg.norm(vec)
        if norm < 2:  # effectively stationary -> ignore, avoids noisy direction flips
            return None
        return vec / norm

    def _in_restricted_zone(self, centroid):
        if self.restricted_zone is None:
            return False
        result = cv2.pointPolygonTest(self.restricted_zone, centroid, False)
        return result >= 0

    def update(self, detections, frame_number, fps):
        """Feed one frame's detections in. Returns per-vehicle status dicts for drawing."""
        timestamp_sec = frame_number / fps if fps > 0 else 0.0
        statuses = []

        for det in detections:
            track_id = det["track_id"]
            cx, cy = det["centroid"]
            self.track_history[track_id].append((cx, cy))
            self.vehicle_type_by_id[track_id] = det["class_name"]

            movement = self._movement_vector(track_id)
            is_wrong_way_now = False
            if movement is not None:
                cosine_sim = float(np.dot(movement, self.normal_direction))
                is_wrong_way_now = cosine_sim < self.direction_threshold

            in_zone_now = self._in_restricted_zone((cx, cy))

            # record each violation type only once per track_id (no duplicate spam)
            if is_wrong_way_now and track_id not in self.wrong_way_ids:
                self.wrong_way_ids.add(track_id)
                self.violation_events.append({
                    "track_id": track_id,
                    "vehicle_type": det["class_name"],
                    "violation_type": "wrong_way",
                    "frame": frame_number,
                    "timestamp_sec": round(timestamp_sec, 2),
                })

            if in_zone_now and track_id not in self.zone_violation_ids:
                self.zone_violation_ids.add(track_id)
                self.violation_events.append({
                    "track_id": track_id,
                    "vehicle_type": det["class_name"],
                    "violation_type": "restricted_zone",
                    "frame": frame_number,
                    "timestamp_sec": round(timestamp_sec, 2),
                })

            statuses.append({
                **det,
                "movement_vector": movement,
                "is_wrong_way": track_id in self.wrong_way_ids,
                "in_restricted_zone": track_id in self.zone_violation_ids,
            })

        return statuses

    def get_stats(self):
        type_counts = defaultdict(int)
        for v in self.vehicle_type_by_id.values():
            type_counts[v] += 1

        return {
            "total_vehicles": len(self.vehicle_type_by_id),
            "total_violations": len(self.violation_events),
            "wrong_way_violations": len(self.wrong_way_ids),
            "restricted_zone_violations": len(self.zone_violation_ids),
            "vehicle_type_counts": dict(type_counts),
            "violation_events": self.violation_events,
        }


# ---------------------------------------------------------------------------
# Drawing — Variant 1: Wrong-Way Detection (movement-focused)
# ---------------------------------------------------------------------------

def draw_variant1(frame, statuses, zone_polygon=None, normal_direction=(0, 1)):
    out = frame.copy()

    if zone_polygon is not None:
        cv2.polylines(out, [np.array(zone_polygon, dtype=np.int32)], True, (0, 165, 255), 2)

    live_violators = 0

    for s in statuses:
        x1, y1, x2, y2 = map(int, s["bbox"])
        cx, cy = map(int, s["centroid"])
        wrong = s["is_wrong_way"]
        if wrong:
            live_violators += 1

        color = (0, 0, 255) if wrong else (0, 200, 0)
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)

        label = f"ID {s['track_id']} {s['class_name']}"
        if wrong:
            label += " WRONG WAY"
        cv2.putText(out, label, (x1, max(y1 - 8, 15)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        if s["movement_vector"] is not None:
            dx, dy = s["movement_vector"]
            tip = (int(cx + dx * 40), int(cy + dy * 40))
            cv2.arrowedLine(out, (cx, cy), tip, color, 2, tipLength=0.4)

    # reference arrow showing what "normal direction" is
    ndx, ndy = normal_direction
    origin = (50, 60)
    tip = (int(50 + ndx * 40), int(60 + ndy * 40))
    cv2.arrowedLine(out, origin, tip, (255, 255, 0), 2, tipLength=0.4)
    cv2.putText(out, "Normal Direction", (70, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1)

    # violation counter banner
    cv2.rectangle(out, (0, 0), (330, 40), (0, 0, 0), -1)
    total_wrong_way_ever = len({s["track_id"] for s in statuses if s["is_wrong_way"]})
    cv2.putText(out, f"Wrong-Way Violations: {total_wrong_way_ever}", (10, 27),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return out


# ---------------------------------------------------------------------------
# Drawing — Variant 2: Traffic Violation Dashboard (analytics-focused)
# ---------------------------------------------------------------------------

def draw_variant2(frame, statuses, stats, zone_polygon=None, panel_width=280):
    out = frame.copy()
    h, w = out.shape[:2]

    if zone_polygon is not None:
        cv2.polylines(out, [np.array(zone_polygon, dtype=np.int32)], True, (0, 165, 255), 2)

    # minimal boxes on the video itself — the dashboard panel carries the info
    for s in statuses:
        x1, y1, x2, y2 = map(int, s["bbox"])
        flagged = s["is_wrong_way"] or s["in_restricted_zone"]
        color = (0, 0, 255) if flagged else (180, 180, 180)
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 1)
        cv2.putText(out, f"{s['track_id']}", (x1, max(y1 - 5, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1)

    panel = np.full((h, panel_width, 3), (25, 25, 25), dtype=np.uint8)

    lines = [
        ("TRAFFIC VIOLATION DASHBOARD", (0, 255, 255)),
        ("", None),
        (f"Total Vehicles: {stats['total_vehicles']}", (255, 255, 255)),
        (f"Total Violations: {stats['total_violations']}", (0, 0, 255)),
        (f"  Wrong-Way: {stats['wrong_way_violations']}", (0, 100, 255)),
        (f"  Restricted Zone: {stats['restricted_zone_violations']}", (0, 165, 255)),
        ("", None),
        ("Vehicle Type Counts:", (255, 255, 255)),
    ]
    for vtype, count in stats["vehicle_type_counts"].items():
        lines.append((f"  {vtype}: {count}", (200, 200, 200)))

    lines.append(("", None))
    lines.append(("Recent Violations:", (255, 255, 255)))
    for e in stats["violation_events"][-6:]:
        lines.append((f"  ID{e['track_id']} {e['violation_type']} @{e['timestamp_sec']}s", (150, 150, 255)))

    lines.append(("", None))
    is_clear = stats["total_violations"] == 0
    status_text = "STATUS: CLEAR" if is_clear else "STATUS: VIOLATIONS DETECTED"
    status_color = (0, 200, 0) if is_clear else (0, 0, 255)
    lines.append((status_text, status_color))

    y = 30
    for text, color in lines:
        if text:
            cv2.putText(panel, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1)
        y += 22

    return np.hstack([out, panel])


# ---------------------------------------------------------------------------
# Zone helper
# ---------------------------------------------------------------------------

def default_restricted_zone(frame_w, frame_h):
    """A generic rectangular restricted zone in the lower-center of the frame."""
    return [
        (int(frame_w * 0.35), int(frame_h * 0.60)),
        (int(frame_w * 0.65), int(frame_h * 0.60)),
        (int(frame_w * 0.65), int(frame_h * 0.95)),
        (int(frame_w * 0.35), int(frame_h * 0.95)),
    ]


# ---------------------------------------------------------------------------
# ffmpeg re-encode (matches the H.264 pattern used throughout this internship
# for browser/Streamlit-Cloud-compatible video output)
# ---------------------------------------------------------------------------

def reencode_h264(input_path, output_path):
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------------------
# End-to-end pipeline
# ---------------------------------------------------------------------------

def process_video(
    input_path,
    output_path,
    variant="wrong_way",          # "wrong_way" or "dashboard"
    model_path="yolov8n.pt",
    normal_direction=(0, 1),
    restricted_zone=None,
    conf=0.3,
    reencode=True,
):
    """
    Runs the full pipeline on a video file:
      detect -> track -> direction check -> zone check -> draw -> write

    Returns the final stats dict from TrafficViolationDetector.get_stats().
    """
    from tracker import VehicleTracker  # lazy import: keeps this module testable without ultralytics installed

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if restricted_zone is None:
        restricted_zone = default_restricted_zone(w, h)

    vehicle_tracker = VehicleTracker(model_path=model_path, conf=conf)
    detector = TrafficViolationDetector(
        normal_direction=normal_direction,
        restricted_zone=restricted_zone,
    )

    out_w = w + 280 if variant == "dashboard" else w
    tmp_output = output_path + ".tmp.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(tmp_output, fourcc, fps, (out_w, h))

    frame_number = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_number += 1

        detections = vehicle_tracker.track_frame(frame)
        statuses = detector.update(detections, frame_number, fps)
        stats_now = detector.get_stats()

        if variant == "wrong_way":
            annotated = draw_variant1(frame, statuses, zone_polygon=restricted_zone,
                                       normal_direction=normal_direction)
        else:
            annotated = draw_variant2(frame, statuses, stats_now, zone_polygon=restricted_zone)

        writer.write(annotated)

    cap.release()
    writer.release()

    if reencode:
        try:
            reencode_h264(tmp_output, output_path)
            os.remove(tmp_output)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # ffmpeg not available -> fall back to the raw mp4v output
            os.replace(tmp_output, output_path)
    else:
        os.replace(tmp_output, output_path)

    return detector.get_stats()
