import os
import cv2
from ultralytics import YOLO


base_dir = os.path.dirname(os.path.abspath(__file__))          # robust path resolution
sample_videos_dir = os.path.join(base_dir, "input videos")     # put your 5 input videos here
output_videos_dir = os.path.join(base_dir, "output_videos")
model_path = "yolov8s.pt"        # small model instead of nano
tracker = "bytetrack.yaml"       # or "botsort.yaml"
conf_thres = 0.15        
image_size = 1280               

os.makedirs(output_videos_dir, exist_ok=True)


def track_video(model: YOLO, video_path: str, output_path: str) -> int:

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  [!] Could not open {video_path}, skipping.")
        return 0

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    unique_ids = set()

    # stream = True + persist = True is what keeps track IDs alive frame-to-frame
    results = model.track(
        source = video_path,
        conf = conf_thres,
        imgsz = image_size,
        tracker = tracker,
        persist = True,
        stream = True,
        verbose = False,
    )

    # scale font/box thickness relative to frame size so labels stay readable

    scale = max(width, height) / 1280
    font_scale = max(0.5 * scale, 0.4)
    thickness = max(int(2 * scale), 1)

    for result in results:
        frame = result.orig_img

        boxes = result.boxes
        if boxes is not None and boxes.id is not None:
            ids = boxes.id.int().cpu().tolist()
            xyxy = boxes.xyxy.cpu().tolist()
            confs = boxes.conf.cpu().tolist()
            clss = boxes.cls.int().cpu().tolist()

            for box, obj_id, conf, cls_id in zip(xyxy, ids, confs, clss):
                unique_ids.add(obj_id)
                x1, y1, x2, y2 = map(int, box)
                label = f"ID {obj_id} {model.names[cls_id]} {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), thickness)
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                cv2.rectangle(frame, (x1, max(y1 - th - 10, 0)), (x1 + tw + 4, y1), (120, 255, 10), -1)
                cv2.putText( frame, label, (x1 + 2, max(y1 - 6, th)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (10, 10, 0), thickness,)


        cv2.putText(frame, f"Unique objects so far: {len(unique_ids)}", (15, int(30 * scale)),cv2.FONT_HERSHEY_SIMPLEX, font_scale * 1.3, (12,134,49), thickness,)

        writer.write(frame)

    cap.release()
    writer.release()
    return len(unique_ids)


def main():
    model = YOLO(model_path)

    videos = [
        f for f in sorted(os.listdir(sample_videos_dir))
        if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
    ]

    if not videos:
        print(f"No videos found in {sample_videos_dir}. Drop at least 5 clips there first.")
        return

    print(f"Found {len(videos)} video(s). Running tracking with '{tracker}'...\n")
    summary = {}

    for video_name in videos:
        in_path = os.path.join(sample_videos_dir, video_name)
        out_name = f"tracked_{os.path.splitext(video_name)[0]}.mp4"
        out_path = os.path.join(output_videos_dir, out_name)

        print(f"-> Processing {video_name} ...")
        unique_count = track_video(model, in_path, out_path)
        summary[video_name] = unique_count
        print(f"   Unique objects tracked: {unique_count}")
        print(f"   Saved: {out_path}\n")

    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for name, count in summary.items():
        print(f"{name:35s} -> {count} unique object(s)")


if __name__ == "__main__":
    main()