# Day 36 — Traffic Violation Monitoring System

YOLOv8 detection + ByteTrack tracking + rule-based direction and zone violation detection, deployed via Streamlit.

## How vehicle tracking works

`tracker.py` wraps `model.track(frame, persist=True, tracker="bytetrack.yaml")`. `persist=True` keeps the
same `VehicleTracker` instance's internal tracker state alive across every frame passed to it, so ByteTrack
can re-associate detections with existing tracks frame-to-frame instead of starting fresh each time. Each
tracked vehicle gets a stable integer `track_id` for its entire time in frame, plus its class
(car/motorcycle/bus/truck via COCO class IDs 2/3/5/7), bounding box, and centroid.

## How direction is calculated

For every tracked vehicle, `TrafficViolationDetector` keeps a rolling history (`deque(maxlen=30)`) of its
centroid positions. Once a track has at least `min_track_len` points, its **movement vector** is computed as
`(latest_position - earliest_position)`, normalized to a unit vector. This is deliberately a "net displacement"
vector rather than frame-to-frame deltas, so it isn't thrown off by pixel-level jitter in a single frame.

## How wrong-way vehicles are identified

The movement vector is compared to a user-defined `normal_direction` unit vector (e.g. `(0, 1)` = top-to-bottom)
using **cosine similarity** (dot product of two unit vectors). A value near `1` means moving with traffic, near
`-1` means moving directly against it. Any vehicle whose cosine similarity drops below `direction_threshold`
(default `-0.3`, i.e. moving noticeably against the flow) is flagged wrong-way.

## How restricted zones are defined

A restricted zone is a polygon of `(x, y)` pixel coordinates. Each frame, `cv2.pointPolygonTest` checks whether
a vehicle's centroid falls inside that polygon. `default_restricted_zone()` auto-generates a rectangle in the
lower-center of the frame if no custom polygon is supplied, so the system works out of the box on any video —
but for real use you'd draw a polygon matching an actual restricted area (e.g. a bus lane, no-entry ramp).

## How duplicate violations are avoided

Each `track_id` can only appear once in `wrong_way_ids` / `zone_violation_ids` — these are Python `set()`s.
Once a vehicle is flagged for a violation type, later frames still show it as "already flagged" in the overlay,
but no second event is appended to `violation_events`. This means a car that drifts in and out of the restricted
zone, or briefly wobbles below the direction threshold, is only counted once — not once per frame.

## How violation statistics are generated

`TrafficViolationDetector.get_stats()` derives everything from the `violation_events` list and the
`vehicle_type_by_id` map that's built up as vehicles are seen: total unique vehicles, total violations,
per-type violation counts, per-vehicle-type counts, and the full timestamped event log. `analytics.py` then
serializes this to JSON/CSV and prints a console summary.

## Difference between the two demo variants

- **Variant 1 (Wrong-Way Detection)** — movement-focused. Full-size video with bounding boxes, IDs, a direction
  arrow drawn on every vehicle, a reference "normal direction" arrow in the corner, wrong-way vehicles highlighted
  red, and a live violation counter banner.
- **Variant 2 (Traffic Violation Dashboard)** — analytics-focused, visually different layout. The video is shown
  smaller/minimal (thin boxes, ID only) alongside a dark side panel showing total vehicles, total violations
  broken down by type, vehicle type counts, a scrolling recent-violations feed, and an overall traffic status
  line. The output frame is wider (`video width + 280px`) to accommodate the panel.

## Challenges and limitations

- **Single global direction assumption** — the system assumes one "normal" direction for the whole frame, which
  works for a straight road segment but breaks down at roundabouts or multi-directional intersections without
  per-lane direction zones.
- **No live camera support by design** — this is a video-file pipeline only, as specified; it does not connect
  to an RTSP/live stream.
- **Aerial/top-down footage** — as found during the parking-detection project earlier in this internship, stock
  YOLOv8n struggles with top-down views. The default confidence threshold and vehicle classes may need tuning
  per video, and a drone-trained model (e.g. VisDrone weights) may be needed for very high-altitude footage.
- **ID switches on occlusion** — like any tracker, ByteTrack can occasionally swap IDs when vehicles overlap
  heavily (e.g. at a busy intersection), which could cause a vehicle to be double-counted as "new."
- **Zone/direction are configured, not learned** — restricted zones and normal direction must be set per video;
  there's no automatic lane/road detection.

## Running locally

```bash
uv run test_run.py
```

This processes every `.mp4` in `input_videos/` through both variants and writes results to
`outputs/variant-1/` and `outputs/variant-2/`, plus a JSON stats file and CSV event log per video.

## Running the Streamlit app

```bash
uv run streamlit run app.py
```

Upload a video, pick a mode (Wrong-Way Detection / Traffic Violation Analytics), set the normal direction,
run, then view/download the processed video and stats.

## Folder structure

```
Day-36/
├── app.py
├── traffic_violation.py
├── tracker.py
├── analytics.py
├── test_run.py
├── requirements.txt
├── packages.txt
├── README.md
├── input_videos/        <- video1.mp4, video2.mp4, video3.mp4 go here
├── sample_videos/
└── outputs/
    ├── variant-1/
    └── variant-2/
```
