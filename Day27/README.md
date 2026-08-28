# Day 29 — Custom Object Detection: Helmet Detection System

## Overview

This project trains a custom YOLOv8 object detection model to identify riders, helmet-wearing status, and number plates in traffic images, then deploys it as an interactive Streamlit application for image and video inference.

## Dataset

**Source:** [Rider, With Helmet, Without Helmet, Number Plate](https://www.kaggle.com/datasets/aneesarom/rider-with-helmet-without-helmet-number-plate) — Kaggle

**Why this dataset:** Most publicly available helmet datasets are single-class (they only flag "no helmet" violations). This dataset was chosen instead because it provides genuine multi-class annotations — separating "with helmet," "without helmet," "rider," and "number plate" as distinct labeled classes — which gives a richer, more realistic rider-safety-compliance detection task rather than a simple binary flag.

**Classes (4):**
| ID | Class |
|----|-------|
| 0 | with helmet |
| 1 | without helmet |
| 2 | rider |
| 3 | number plate |

**Splits:**
- Train: ~100 images
- Validation: 20 images
- **No separate test split was provided with this dataset.** The validation set was used both for validation-during-training and for final evaluation / sample inference, since no held-out test set exists. This is noted here for transparency — metrics reported below are validation metrics, not a true held-out test score.

**Data cleaning performed:**
- One corrupt file (`new3.jpg`, actually a GIF mislabeled as `.jpg`) was automatically skipped by Ultralytics during dataset scanning.
- Several orphaned label files (`.txt` label files with no matching image, e.g. `new128.txt`) were found and removed via a small cleanup script before training, to prevent `FileNotFoundError` crashes mid-epoch.

## Training Configuration

| Parameter | Value |
|---|---|
| Base model | `yolov8n.pt` (YOLOv8 nano, pretrained on COCO — transfer learning) |
| Epochs | 23 |
| Batch size | 8 |
| Image size | 640×640 |
| Device | CPU (Intel i7-1185G7, integrated GPU — no CUDA support) |
| Optimizer | AdamW (auto-selected) |
| Training time | ~14.4 minutes (0.24 hours) |

Training was run locally (no GPU), using the `ultralytics` Python package. An initial short run (4 epochs) was used first to validate the full pipeline end-to-end before committing to a longer training run.

## Evaluation Metrics (final model, validation set)

| Class | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|
| **All (overall)** | 0.92 | 0.86 | **0.934** | 0.754 |
| with helmet | 0.989 | 0.769 | 0.922 | 0.744 |
| without helmet | 0.799 | 0.800 | 0.902 | 0.740 |
| rider | 0.939 | 0.913 | 0.920 | 0.742 |
| number plate | 0.955 | 0.957 | 0.993 | 0.790 |

**Target: mAP@50 ≥ 80% — achieved (93.4% overall, every individual class above 90%).**

### Training progression
The model was trained in stages to observe learning behavior:
- Epoch 1: mAP50 = 0.232 (model has barely started learning)
- Epoch 6: mAP50 = 0.866
- Epoch 11: mAP50 = 0.927
- Epoch 23 (final): mAP50 = 0.934

Loss values (`box_loss`, `cls_loss`, `dfl_loss`) decreased steadily and consistently across training, with no signs of divergence.

## Inference

Inference was run on a held-out sample of images taken from the validation set (`test_samples/` folder) using `inference.py`. Detections were printed with class name and confidence score, and annotated images (with bounding boxes drawn) were saved automatically via Ultralytics' `save=True` option.

Example output format:
```
Image: test_samples/img1.jpg
  Detected: rider — confidence: 0.94
  Detected: without helmet — confidence: 0.81
```

## Challenges Faced & Improvements

1. **Orphaned labels / corrupt files.** The raw dataset contained a mislabeled GIF file and several label files with no matching image, both of which crashed training initially. Fixed by writing a small script to detect and remove orphaned labels before training, and letting Ultralytics auto-skip the corrupt image.

2. **`data.yaml` path handling.** Early training attempts failed due to relative paths in `data.yaml` not resolving as expected from the script's working directory. This was resolved by switching to explicit absolute paths for `train`, and `val`.

3. **Small dataset size (~100 training images).** With so few images, single-class recall was volatile in early epochs (e.g., "with helmet" and "without helmet" both had 0% recall at epoch 2, despite high precision) before stabilizing by epoch 6 onward. This is a known effect of small dataset size, and more epochs (14 → 23) meaningfully improved mAP50 (92.9% → 93.4%) and, more notably, mAP50-95 (72.0% → 75.4%), indicating better bounding box precision, not just more correct classifications.

4. **Gap between validation metrics and real-world generalization.** Despite strong validation mAP50 (>90% across all classes), testing the model on a new, unseen image outside the dataset showed it correctly detected "rider" instances but **missed the "with helmet" detection** that was visually obvious to a human. This highlights an important lesson: validation metrics on a small (20-image) validation set can be optimistic compared to true generalization performance. Likely causes include the limited training set size, and differences in image quality/compression between training data and the new test image. This suggests that scaling up the dataset and adding data augmentation (rotation, brightness/contrast variation, blur) would likely improve real-world robustness beyond what the validation numbers alone suggest.

5. **CPU-only local training.** No CUDA-capable GPU was available (integrated GPU only), so all training ran on CPU. This made each epoch take 25–35 seconds, keeping full training runs to a manageable ~15–20 minutes for this dataset size — but this approach would not scale well to a larger dataset without GPU acceleration.

## Deployment

A Streamlit application (`app.py`) was built to demonstrate the trained model interactively:
- **Image mode:** upload an image, view the original and detected image side-by-side, see per-object confidence scores, and download the annotated result.
- **Video mode:** upload a video, run frame-by-frame detection with a progress indicator, re-encode the output to H.264 (via `imageio-ffmpeg`) for browser compatibility, and download the processed video.
- A live confidence-threshold slider allows adjusting detection sensitivity without editing code.

### Running the app locally
```bash
uv pip install streamlit ultralytics opencv-python-headless imageio-ffmpeg
uv run streamlit run app.py
```

## Repository Structure

```
Day-29/
├── training_script.py       # YOLO training script
├── inference.py              # Runs inference on test images, prints confidence scores
├── app.py                    # Streamlit deployment app
├── requirements.txt
├── README.md
├── test_samples/              # Sample images used for inference/testing
├── runs/detect/.../weights/
│   ├── best.pt                # Final trained model (used in app + inference)
│   └── last.pt
└── prediction_results/        # Saved annotated output images
```

## Deliverables

- [ ] GitHub Repository Link:
- [ ] App Public URL:
- [ ] Screen recording (3–5 min):
- [ ] Public model output video URL:

## Summary

This project trained a 4-class YOLOv8 object detection model (with helmet, without helmet, rider, number plate) achieving 93.4% mAP@50 on the validation set — exceeding the 80% target — using a small (~100 image) dataset trained locally on CPU in ~15 minutes. The model was deployed via a Streamlit app supporting both image and video inference. The main lesson from this project was the gap between strong validation metrics and real-world generalization on unseen images, pointing toward dataset size and augmentation as the next areas for improvement.