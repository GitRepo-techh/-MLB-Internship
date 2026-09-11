# 🚗 Smart Vehicle Counter

YOLOv8 detection + multi-object tracking that counts vehicles crossing a
user-defined line in a video, built as an upgrade of an earlier line-crossing
counter (Day 31) for the **Day 39: Model & Application Optimization** task of
the MLB Internship.

![App screenshot](assets/app-screenshot.png)

## Features

- 🎚️ **Adjustable confidence & IoU thresholds** — tune detection sensitivity live from the sidebar, no code edits needed
- 📏 **Interactive ROI / counting line** — drag sliders to place the line anywhere in the frame, with a live preview before processing
- 🔁 **Consistent IDs across crossings** — choice of ByteTrack (fast) or a tuned BoT-SORT config (`trackers/botsort_stable.yaml`) that survives brief occlusion, so a vehicle keeps its ID even when another one crosses close in front of it
- 📊 **CSV crossing report** — every counted vehicle logged with ID, class, frame, timestamp, and direction
- ⏳ **Live progress bar** during video processing
- 🖼️ **Image and video support** — video mode does line-crossing counting, image mode does straight per-class detection counts
- ⬇️ **One-click downloads** for the processed video, annotated image, and CSV report
- 🎨 **Cleaner visualization** — per-class colors, motion trails, and a semi-transparent stats overlay instead of raw text-on-frame
- 🛡️ **Error handling** around file I/O, the tracker, and video re-encoding, surfaced as readable messages instead of crashes

## Tech stack

| Component | Tool |
|---|---|
| Object detection | YOLOv8n (Ultralytics, COCO-pretrained) |
| Multi-object tracking | ByteTrack / BoT-SORT |
| Video/image processing | OpenCV |
| Browser-compatible video output | ffmpeg (via `imageio_ffmpeg`) re-encode to H.264 |
| UI | Streamlit |
| Package management | `uv` |

## Project structure

```
Day-39/
├── app.py                       # Streamlit UI
├── vehicle_counter.py           # Core detection/tracking/counting logic
├── trackers/
│   └── botsort_stable.yaml      # Tuned BoT-SORT config for stable IDs
├── requirements.txt
├── sample_input/                # Example input video(s)
├── sample_output/               # Example processed video(s) + CSV
└── README.md
```

## Installation

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd Day-39

# using uv (recommended)
uv sync

# or with plain pip
pip install -r requirements.txt
```

You'll also need **ffmpeg** available on your PATH (used to re-encode output
video to browser-playable H.264).

## Usage

Run the Streamlit app:

```bash
uv run streamlit run app.py
# or: streamlit run app.py
```

1. Choose **Video** or **Image** as the input type and upload a file.
2. **Video mode:** drag the four sliders under *"Set the counting line"*
   until the yellow line in the preview sits where you want vehicles to be
   counted, then click **Process video**.
3. **Image mode:** click **Detect vehicles** to get per-class detection
   counts on a single frame.
4. Review the results (per-class counts, annotated output, and — for video —
   the crossing log table) and use the download buttons to save the
   processed video / image / CSV report.

Detection sensitivity (confidence, IoU) and the tracker used for ID
consistency can be adjusted anytime from the sidebar before processing.

## How it works

Each frame is run through YOLOv8 with `model.track(persist=True, ...)`,
which detects vehicles and assigns each one a persistent ID using either
ByteTrack or BoT-SORT. A vehicle's centroid is compared frame-to-frame
against the counting line using a cross-product side check (so the line can
be horizontal, vertical, or diagonal); when its side flips, that's counted
as one crossing, and the ID is marked so it's never double-counted. The
BoT-SORT config keeps "lost" tracks alive for longer (60 frames vs the
default 30), which is what keeps a vehicle's ID intact through brief
occlusion — like another vehicle crossing close in front of it — instead of
issuing a new ID when it reappears.

## Known limitations

- Counting line is currently straight (two points), not a full polygonal ROI
- BoT-SORT here uses motion-based re-identification only; true
  appearance-based ReID would need an additional ReID model, which was left
  out to keep the app lightweight and easy to deploy
- Heavy occlusion (vehicles fully overlapping for a long stretch) can still
  occasionally cause an ID switch even with BoT-SORT
- Counting accuracy depends on video quality/frame rate — low-FPS or
  heavily compressed footage can cause missed crossings

## Demo

- 🎥 Demo video: `<ADD YOUR 3–5 MIN DEMO VIDEO LINK HERE>`
- 🌐 Live app: `<ADD YOUR STREAMLIT CLOUD / HUGGING FACE SPACE URL HERE>`
- 💻 GitHub repo: `<ADD YOUR GITHUB REPO LINK HERE>`

## License

MIT — see [LICENSE](LICENSE) for details.
