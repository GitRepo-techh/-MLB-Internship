import os
import cv2
from ultralytics import YOLO


MODEL_NAME = "yolov8n.pt"        # nano model — fast, good for CPU
CONF_THRESHOLD = 0.4

INPUT_IMAGES_DIR = "input images"
INPUT_VIDEOS_DIR = "input videos"

OUTPUT_IMAGES_DIR = "output/images"
OUTPUT_VIDEOS_DIR = "output/videos"

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
VIDEO_EXTS = (".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv", ".flv", ".m4v")


def run_on_images(model: YOLO) -> None:


    os.makedirs(OUTPUT_IMAGES_DIR, exist_ok=True)

    if not os.path.isdir(INPUT_IMAGES_DIR):
        print(f"[!] '{INPUT_IMAGES_DIR}' folder not found — skipping images.")
        return

    image_files = [f for f in os.listdir(INPUT_IMAGES_DIR) if f.lower().endswith(IMAGE_EXTS)]

    if not image_files:
        print(f"[!] No images found in '{INPUT_IMAGES_DIR}'.")
        return


    for filename in image_files:
        img_path = os.path.join(INPUT_IMAGES_DIR, filename)

        # Inference: preprocessing + forward pass + NMS all happen inside this call
        results = model(img_path, conf=CONF_THRESHOLD, verbose=False)

        for r in results:
            # r.plot() returns a BGR numpy array with boxes/labels/scores drawn on it
            annotated = r.plot()
            out_path = os.path.join(OUTPUT_IMAGES_DIR, filename)
            cv2.imwrite(out_path, annotated)

            print(f"\n{filename} to {len(r.boxes)} object(s) detected")
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id]
                conf = float(box.conf[0])
                x1, y1, x2, y2 = [round(v, 1) for v in box.xyxy[0].tolist()]
                print(f"  - {cls_name:<15} conf={conf:.2f}  box=({x1}, {y1}, {x2}, {y2})")

    print(f"\nSaved annotated images to '{OUTPUT_IMAGES_DIR}/'")


def run_on_videos(model: YOLO) -> None:
    """Run detection on every video in INPUT_VIDEOS_DIR, save annotated copies."""
    os.makedirs(OUTPUT_VIDEOS_DIR, exist_ok=True)

    if not os.path.isdir(INPUT_VIDEOS_DIR):
        print(f"[!] '{INPUT_VIDEOS_DIR}' folder not found — skipping videos.")
        return

    all_files = os.listdir(INPUT_VIDEOS_DIR)
    video_files = [f for f in all_files if f.lower().endswith(VIDEO_EXTS)]
    skipped = [f for f in all_files if f not in video_files]

    if skipped:
        print(f"[i] Files in '{INPUT_VIDEOS_DIR}' NOT recognized as videos (check extension): {skipped}")

    if not video_files:
        print(f"[!] No videos found in '{INPUT_VIDEOS_DIR}'.")
        return

    print(f"\n=== Running detection on {len(video_files)} video(s) ===")

    for filename in video_files:
        vid_path = os.path.join(INPUT_VIDEOS_DIR, filename)
        name_no_ext = os.path.splitext(filename)[0]

        cap = cv2.VideoCapture(vid_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        out_path = os.path.join(OUTPUT_VIDEOS_DIR, f"{name_no_ext}_detected.mp4")
        writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

        frame_count = 0
        class_counts = {}

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame, conf=CONF_THRESHOLD, verbose=False)
            annotated = results[0].plot()
            writer.write(annotated)

            for box in results[0].boxes:
                cls_name = model.names[int(box.cls[0])]
                class_counts[cls_name] = class_counts.get(cls_name, 0) + 1

            frame_count += 1

        cap.release()
        writer.release()

        print(f"\n{filename} -> {frame_count} frames processed")
        print(f"  Class detections across all frames: {class_counts}")
        print(f"  Saved to '{out_path}'")


def main():
    print(f"Loading model: {MODEL_NAME} ...")
    model = YOLO(MODEL_NAME)
    print(f"Model loaded. Classes: {len(model.names)} (COCO pretrained)")

    run_on_images(model)
    run_on_videos(model)

    print("\nDone.")


if __name__ == "__main__":
    main()