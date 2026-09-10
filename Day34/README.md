# Day 38 — Intelligent Security Monitoring + Image Segmentation Deployment

## Contents

- `security_monitoring/security_monitor.py` — Coding Practice: YOLOv8 + ByteTrack
  person detection/tracking with custom ROIs, entry/exit event detection,
  CSV event logging, and live active-count overlay.
- `segmentation_app/app.py` — Deployment Task: Streamlit app for Binary,
  Adaptive, and Otsu thresholding, with upload, method selection, side-by-side
  view, and download.
- `sample_images/` — sample input images used for testing segmentation.
- `output_images/` — segmented output images produced by the app.
- `requirements.txt` — dependencies for both parts.

## Part 1 — Coding Practice: Security Monitoring

```bash
uv add ultralytics opencv-python-headless imageio-ffmpeg lap
uv run security_monitoring/security_monitor.py --input input_videos/video1.mp4
```

Edit `ROI_DEFINITIONS` at the top of `security_monitor.py` to set your own
region(s) — each is a polygon of `(x_fraction, y_fraction)` points, so it
scales automatically to any video resolution.

Output:
- An annotated video showing ROI outlines, tracked person boxes/IDs, and a
  live "active people" count per region.
- A CSV (`event_logs/<video>_events.csv`) with one row per completed
  entry/exit: `track_id, region, entry_time, exit_time, duration_seconds`.
  Duplicate alerts are avoided by only logging a state *change*
  (enter or exit), never a per-frame repeat while someone stays inside.

## Part 2 — Deployment Task: Image Segmentation Studio

```bash
uv add streamlit pillow numpy opencv-python-headless
uv run streamlit run segmentation_app/app.py
```

Then expose it publicly with ngrok:

```bash
ngrok http 8501
```

Copy the `https://....ngrok-free.app` URL it prints — that's the public
Streamlit URL to submit for evaluation, alongside the GitHub repo link.
Keep the `streamlit run` and `ngrok` processes both running while it's
being evaluated.

### What is image segmentation?

Image segmentation is the process of partitioning an image into regions
(commonly foreground vs. background, or object vs. non-object) so that each
pixel is assigned to a meaningful group. Thresholding is the simplest form
of segmentation: it separates pixels purely by intensity value.

### Binary vs. Adaptive vs. Otsu Thresholding

| Method | How it works | Best for |
|---|---|---|
| **Binary** | One fixed threshold value, chosen manually, applied to every pixel in the image. | Images with even, consistent lighting where you already know a good cutoff. |
| **Adaptive** | Computes a *local* threshold for each small neighborhood (block) of the image, based on the pixel intensities around it. | Images with uneven lighting, shadows, or gradients, where one global cutoff fails in some regions. |
| **Otsu** | Automatically calculates the single *global* threshold that best splits the image's intensity histogram into two classes (foreground/background), minimizing within-class variance. | Images with a clear bimodal histogram (two distinct intensity peaks) and mostly even lighting — no manual tuning needed. |

### Which method worked best for your dataset and why

*(Fill in after testing — with the app running, upload each sample image
and compare the three methods with `st.info` showing the exact threshold
each one picked. As a general pattern to expect: Otsu tends to win on
evenly-lit images with a clear subject/background split, since it removes
the guesswork of Binary while still being a single global cutoff; Adaptive
tends to win on images with shadows or uneven lighting, since Binary and
Otsu both apply one number to the whole image and will lose detail in the
darker/brighter regions.)*

### Challenges faced during implementation

*(Fill in based on your actual run — e.g. block size in Adaptive
thresholding must be odd, so the app auto-corrects even values; Otsu
benefits from a light Gaussian blur first to reduce noise before computing
the histogram split, which is why it's applied before `cv2.threshold`
in this app.)*
