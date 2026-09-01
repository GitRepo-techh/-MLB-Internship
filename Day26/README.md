# Day 26 — Document & Object Segmentation Tool

A Streamlit app for segmenting documents/objects from their background using
Binary, Adaptive, and Otsu thresholding, plus Watershed and GrabCut.

## What is Image Segmentation?

Image segmentation is the process of dividing an image into meaningful regions
by classifying each **pixel**, rather than just drawing a box around an object
(as in object detection). This pixel-level precision makes it essential for
tasks like medical scans, document scanning, and background removal.

## Binary vs Adaptive vs Otsu Thresholding

| Method | How it works | Best for |
|---|---|---|
| **Binary** | One fixed threshold value applied to every pixel | Clean, evenly-lit images |
| **Adaptive** | Threshold is recalculated per local region (block) | Images with shadows/uneven lighting |
| **Otsu** | Threshold is auto-calculated from the image's histogram (no manual value needed) | Images with a clear bimodal histogram (distinct foreground/background) |

## Which Method Worked Best on My Dataset?

*(Fill this in after running `coding_practice.py` on your 15 images — use the
Otsu threshold values it prints and compare the `*_comparison.png` outputs.)*

Generally:
- **Documents / plain backgrounds** → Otsu worked best, since these images have a
  clearly separated foreground and background in the histogram.
- **Uneven lighting / shadow images** → Adaptive thresholding held up better,
  since Binary and Otsu use one global value and lose detail in shadowed regions.

Replace this section with the actual method + a one-line reason once you've
compared your own `output_images/` results.

## Challenges Faced

- Choosing a fixed threshold for Binary thresholding required trial and error,
  and it broke down completely on shadowed images.
- Adaptive thresholding needed tuning of `block_size` and `C` — too small a
  block picked up noise, too large lost fine detail.
- GrabCut's default rectangle assumes the subject fills most of the frame,
  so it under-segmented images where the object was small or off-center.
- Watershed occasionally over-segmented images with textured backgrounds,
  splitting one object into multiple regions.

## Files

- `segmentation.py` — core segmentation logic
- `coding_practice.py` — batch script for the practice tasks (reads `input_images/`, writes `output_images/`)
- `app.py` — Streamlit mini-project app
- `requirements.txt` — dependencies
- `.streamlit/config.toml` — app theme

## Run Locally

```
uv run coding_practice.py
uv run streamlit run app.py
```