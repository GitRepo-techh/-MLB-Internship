# Day 31 — Smart Vehicle Counting System

A YOLOv8-based system that detects, tracks, and counts vehicles (cars,
motorcycles, buses, trucks) as they cross a defined line in traffic video,
with a Streamlit interface for upload, processing, and download.

## Folder Contents

- `vehicle_counter.py` — core detection, tracking, and counting logic
- `app.py` — Streamlit application (upload → process → view/download)
- `requirements.txt` — Python dependencies
- `packages.txt` — system dependency (ffmpeg) for Streamlit Cloud
- `sample_videos/` — input traffic clips used for testing
- `output_videos/` — processed videos with counts overlaid

## How Vehicle Counting Works

Vehicle counting doesn't mean counting every detection in every frame —
that would count the same vehicle dozens of times as it moves through the
video. Instead, a **counting line** is drawn across the road, and a
vehicle is only counted once, at the moment its center point (centroid)
crosses that line.

Each frame, the model detects vehicles and computes the centroid of each
bounding box. If a vehicle's centroid was on one side of the line in the
previous frame and is on the other side in the current frame, that counts
as a "crossing," and the relevant class counter is incremented.

## How Tracking IDs Prevent Duplicate Counting

Detection alone has no memory — every frame is treated independently, so
the same physical vehicle would trigger a new "crossing" repeatedly as it
sits near the line across several frames. YOLOv8's built-in tracker
(`model.track(persist=True)`) solves this by assigning each vehicle a
persistent ID that stays the same across frames, using motion and
appearance to re-identify it.

With IDs, a `counted_ids` set can be checked before incrementing any
counter — once a given track ID has been counted, it is never counted
again, no matter how many more frames it lingers near the line.

## Vehicle Types Counted

Using COCO class IDs, the system detects and separately counts:
- Car
- Motorcycle
- Bus
- Truck

Counts are tracked per class and displayed live on the video and in the
Streamlit app.

## Challenges Faced

*(Fill this in based on your own testing — a few common ones to check
for and describe in your own words):*
- Vehicles briefly occluded by other vehicles can lose their track ID and
  get re-assigned a new one, causing occasional double-counts.
- Choosing the right line position/height matters — too close to the
  frame edge, and fast-moving vehicles can skip past the line between
  frames without being detected as "crossing."
- mp4v-encoded output isn't playable directly in-browser, so the video
  needs to be re-encoded to H.264 via ffmpeg before it can be shown in
  Streamlit or downloaded reliably.
- Class confusion at a distance (e.g., car vs. small truck) at lower
  confidence thresholds.

## Deployment

- GitHub Repository Link: _add your link_
- Hugging Face Space / Streamlit URL: _add your link_

## Notes on Deployment

- Model weights (`yolov8n.pt`) auto-download on first run via Ultralytics.
- `opencv-python-headless` is used instead of `opencv-python` to avoid
  `libGL` errors on Streamlit Cloud.
- `packages.txt` must sit at the repository root (not inside `Day-31/`)
  if deploying directly from this folder as the app root, so Streamlit
  Cloud installs ffmpeg correctly.