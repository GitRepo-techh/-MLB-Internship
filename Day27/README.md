# Day 27 — Object Detection with YOLO

## Overview
This day introduces object detection using a pretrained YOLOv8 model. It includes a
practice script for batch inference on images and videos, and a Streamlit web app —
**Smart Object Detection** — that lets a user upload an image or video, run detection,
and download the annotated result.

---

## What is Object Detection?

Object detection is the task of identifying **what** objects are present in an image
*and* **where** they are located. Unlike image classification, which assigns a single
label to an entire image, object detection outputs multiple **bounding boxes**, each
paired with a **class label** and a **confidence score** — one for every object found
in the scene. It sits between classification (label only) and segmentation
(label + exact pixel-level mask), giving spatial location without full pixel precision.

## How YOLO Differs from Image Classification

A classifier answers "what is this image of?" with one answer for the whole image.
YOLO ("You Only Look Once") instead divides the image into a grid and, in a single
forward pass, simultaneously predicts for each region:
- whether an object is present (objectness),
- the bounding box coordinates of that object,
- and which class it belongs to, with a confidence score.

Because it does this in one pass rather than scanning the image multiple times with
separate region-proposal and classification stages, YOLO is fast enough to run in
real time on video — which is what makes it usable for the video pipeline in this
project's app, rather than just static images.

## Model Used

**YOLOv8n** (`yolov8n.pt`) — the "nano" variant from Ultralytics, pretrained on the
COCO dataset (80 object classes). It was chosen for its speed on CPU, which matters
for running inference frame-by-frame on video without a GPU.

## Objects Detected

Using the pretrained COCO weights, the application successfully detected a range of
everyday classes across the test images and videos, including: **person, car, boat,
umbrella, horse**, and other standard COCO categories, each with a distinct bounding
box color and a confidence score displayed above the box.

## Challenges Faced

- **Video files not being picked up by the script** — turned out to be a file
  extension mismatch (Explorer was hiding extensions, and the initial script only
  checked for `.mp4/.mov/.avi/.mkv`). Fixed by widening the accepted extension list and
  adding debug logging that prints any unrecognized file found in the input folder.
- **Processed video not playing in the Streamlit app** — OpenCV's `VideoWriter` with
  the `mp4v` fourcc encodes MPEG-4 Part 2, which most browsers' `<video>` element
  cannot decode, resulting in a blank/black player even though detection worked
  correctly. Fixed by re-encoding the output to H.264 (`libx264`) with `ffmpeg` (via
  `imageio-ffmpeg`) immediately after writing, before serving it to the browser.
- Balancing the confidence threshold — too low produced noisy/duplicate boxes on
  some frames, too high dropped smaller or partially occluded objects (e.g. the
  umbrella in rainy, low-contrast footage).

---

## Project Structure

```
Day-27/
├── input images/            # sample input images (10+)
├── input videos/            # sample input videos (2)
├── output/
│   ├── images/               # annotated output images
│   └── videos/               # annotated output videos
├── yolo_practice.py          # batch inference practice script
├── app.py                    # Streamlit Smart Object Detection app
├── requirements.txt
└── README.md
```

## How to Run

```bash
uv sync
uv run python yolo_practice.py     # batch practice script
uv run streamlit run app.py        # interactive app
```

## Links

- **GitHub Repository:** _[add link]_
- **Streamlit Public URL:** _[add link]_
- **Screen Recording (3–5 min demo):** _[add link]_