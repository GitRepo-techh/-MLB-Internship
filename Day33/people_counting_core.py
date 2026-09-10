import os
import argparse
import subprocess
import cv2
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = "yolov8n.pt"     # swap to yolov8s.pt / yolov8m.pt for denser crowds
PERSON_CLASS_ID = 0           # COCO class 0 = person
CONF_THRESHOLD = 0.35


def reencode_h264(raw_path: str, final_path: str) -> None:

    cmd = [
        "ffmpeg", "-y", "-i", raw_path,
        "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        final_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    os.remove(raw_path)


def run_people_counting(input_path: str, output_path: str) -> dict:
    model = YOLO(MODEL_PATH)

    raw_path = output_path.replace(".mp4", "_raw.mp4")

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()  # model.track() below opens the source itself

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(raw_path, fourcc, fps, (width, height))

    unique_ids = set()
    max_count = 0
    frame_num = 0

    # persist=True keeps the same tracker state (and therefore the same IDs)
    # alive across every frame of the stream.
    results_stream = model.track(
        source=input_path,
        classes=[PERSON_CLASS_ID],
        conf=CONF_THRESHOLD,
        persist=True,
        tracker="bytetrack.yaml",
        stream=True,
        verbose=False,
    )

    for result in results_stream:
        frame = result.orig_img.copy()
        frame_num += 1

        boxes = result.boxes
        current_count = 0

        if boxes is not None and boxes.id is not None:
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            ids = boxes.id.cpu().numpy().astype(int)

            current_count = len(ids)
            max_count = max(max_count, current_count)

            for (x1, y1, x2, y2), conf, track_id in zip(xyxy, confs, ids):
                unique_ids.add(track_id)
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
                label = f"ID {track_id} | {conf:.2f}"
                cv2.putText(frame, label, (x1, max(y1 - 8, 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 2)

        # live overlay
        cv2.rectangle(frame, (0, 0), (330, 75), (0, 0, 0), -1)
        cv2.putText(frame, f"Live Count: {current_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Max Count: {max_count}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        writer.write(frame)

    writer.release()
    reencode_h264(raw_path, output_path)

    stats = {
        "frames": frame_num,
        "unique_people": len(unique_ids),
        "max_count": max_count,
        "output_path": output_path,
    }

    print(f"Frames processed     : {stats['frames']}")
    print(f"Unique people tracked: {stats['unique_people']}")
    print(f"Peak occupancy       : {stats['max_count']}")
    print(f"Output saved to      : {stats['output_path']}")

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Day 37 people counting/tracking")
    parser.add_argument("--input", required=True, help="Path to input video")
    parser.add_argument("--output", default=None, help="Path to save output video")
    args = parser.parse_args()

    out = args.output or os.path.join(
        BASE_DIR, "output_videos",
        os.path.splitext(os.path.basename(args.input))[0] + "_counted.mp4",
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    run_people_counting(args.input, out)
