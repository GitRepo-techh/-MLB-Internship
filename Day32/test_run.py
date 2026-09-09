import os
import glob

from traffic_violation import process_video
from analytics import save_stats_json, save_events_csv, print_summary

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input_videos")
OUT_V1_DIR = os.path.join(BASE_DIR, "outputs", "variant-1")
OUT_V2_DIR = os.path.join(BASE_DIR, "outputs", "variant-2")

MODEL_PATH = "yolov8n.pt"  # auto-downloads on first run

# NOTE: normal_direction is a unit-ish vector (dx, dy) in image coordinates
# (x: right is positive, y: DOWN is positive, since that's how pixel rows work).
# (0, 1)  = normal traffic flows DOWNWARD the frame (top -> bottom)
# (0, -1) = normal traffic flows UPWARD the frame (bottom -> top)
# (1, 0)  = normal traffic flows RIGHT
# Adjust per video based on what you actually see when you watch it once.
VIDEO_CONFIGS = {
    "video1.mp4": {"normal_direction": (0, 1)},
    "video2.mp4": {"normal_direction": (0, 1)},
    "video3.mp4": {"normal_direction": (0, 1)},
}


def main():
    os.makedirs(OUT_V1_DIR, exist_ok=True)
    os.makedirs(OUT_V2_DIR, exist_ok=True)

    video_paths = sorted(glob.glob(os.path.join(INPUT_DIR, "*.mp4")))
    if not video_paths:
        print(f"No .mp4 files found in {INPUT_DIR}")
        return

    for video_path in video_paths:
        filename = os.path.basename(video_path)
        cfg = VIDEO_CONFIGS.get(filename, {"normal_direction": (0, 1)})
        name_no_ext = os.path.splitext(filename)[0]

        print(f"\n>>> Processing {filename} ...")

        # ---- Variant 1: Wrong-Way Detection ----
        out1_path = os.path.join(OUT_V1_DIR, f"{name_no_ext}_wrongway.mp4")
        stats1 = process_video(
            input_path=video_path,
            output_path=out1_path,
            variant="wrong_way",
            model_path=MODEL_PATH,
            normal_direction=cfg["normal_direction"],
        )
        print_summary(stats1, label=f"{filename} - Variant 1 (Wrong-Way)")
        save_stats_json(stats1, os.path.join(OUT_V1_DIR, f"{name_no_ext}_stats.json"))
        save_events_csv(stats1, os.path.join(OUT_V1_DIR, f"{name_no_ext}_events.csv"))

        # ---- Variant 2: Traffic Violation Dashboard ----
        out2_path = os.path.join(OUT_V2_DIR, f"{name_no_ext}_dashboard.mp4")
        stats2 = process_video(
            input_path=video_path,
            output_path=out2_path,
            variant="dashboard",
            model_path=MODEL_PATH,
            normal_direction=cfg["normal_direction"],
        )
        print_summary(stats2, label=f"{filename} - Variant 2 (Dashboard)")
        save_stats_json(stats2, os.path.join(OUT_V2_DIR, f"{name_no_ext}_stats.json"))
        save_events_csv(stats2, os.path.join(OUT_V2_DIR, f"{name_no_ext}_events.csv"))

    print("\nAll videos processed. Check outputs/variant-1/ and outputs/variant-2/.")


if __name__ == "__main__":
    main()
