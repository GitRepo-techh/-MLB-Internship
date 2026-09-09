"""
tracker.py
----------
Thin wrapper around Ultralytics YOLOv8 + ByteTrack.

Detects vehicles (car, motorcycle, bus, truck) in a frame and assigns
each one a persistent tracking ID across frames using model.track(persist=True).
"""

from ultralytics import YOLO

# COCO class IDs for vehicle categories (used by stock yolov8n.pt / yolov8s.pt)
VEHICLE_CLASS_IDS = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


class VehicleTracker:
    def __init__(self, model_path="yolov8n.pt", conf=0.3, iou=0.5, tracker_cfg="bytetrack.yaml"):
        self.model = YOLO(model_path)
        self.conf = conf
        self.iou = iou
        self.tracker_cfg = tracker_cfg

    def track_frame(self, frame):
        """
        Run detection + tracking on a single frame.

        Returns a list of dicts:
            {
                "track_id": int,
                "class_id": int,
                "class_name": str,
                "bbox": (x1, y1, x2, y2),
                "centroid": (cx, cy),
                "conf": float,
            }
        """
        results = self.model.track(
            frame,
            persist=True,
            conf=self.conf,
            iou=self.iou,
            classes=list(VEHICLE_CLASS_IDS.keys()),
            tracker=self.tracker_cfg,
            verbose=False,
        )

        detections = []
        r = results[0]

        if r.boxes is not None and r.boxes.id is not None:
            xyxy = r.boxes.xyxy.cpu().numpy()
            ids = r.boxes.id.cpu().numpy().astype(int)
            cls = r.boxes.cls.cpu().numpy().astype(int)
            confs = r.boxes.conf.cpu().numpy()

            for box, track_id, class_id, conf_score in zip(xyxy, ids, cls, confs):
                x1, y1, x2, y2 = box
                cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
                detections.append({
                    "track_id": int(track_id),
                    "class_id": int(class_id),
                    "class_name": VEHICLE_CLASS_IDS.get(int(class_id), "vehicle"),
                    "bbox": (float(x1), float(y1), float(x2), float(y2)),
                    "centroid": (float(cx), float(cy)),
                    "conf": float(conf_score),
                })

        return detections
