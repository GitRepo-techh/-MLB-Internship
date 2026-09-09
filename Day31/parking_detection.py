import cv2
import numpy as np
from ultralytics import YOLO
from huggingface_hub import hf_hub_download


# ---------------------------------
# Geo-trax vehicle classes
# ---------------------------------
# 0 = car
# 1 = bus
# 2 = truck
# 3 = motorcycle

VEHICLE_CLASSES = [0, 1, 2, 3]


class ParkingDetector:

    def __init__(self):

        # Download Geo-trax aerial vehicle detector
        weights = hf_hub_download(
            repo_id="rfonod/geo-trax",
            filename="geotrax_hbb_yolov8s_1920_v1.pt"
        )

        self.model = YOLO(weights)

        self.track_colors = {}


    # ---------------------------------
    # Check if point is inside parking space
    # ---------------------------------

    def point_inside_polygon(self, point, polygon):

        polygon = np.array(
            polygon,
            dtype=np.int32
        )

        return cv2.pointPolygonTest(
            polygon,
            point,
            False
        ) >= 0


    # ---------------------------------
    # Calculate vehicle/polygon overlap
    # ---------------------------------

    def calculate_overlap(self, box, polygon):

        x1, y1, x2, y2 = box

        x1 = max(0, x1)
        y1 = max(0, y1)

        x2 = max(x1 + 1, x2)
        y2 = max(y1 + 1, y2)

        width = x2 - x1 + 1
        height = y2 - y1 + 1

        # Vehicle mask
        vehicle_mask = np.zeros(
            (height, width),
            dtype=np.uint8
        )

        cv2.rectangle(
            vehicle_mask,
            (0, 0),
            (width - 1, height - 1),
            255,
            -1
        )

        # Polygon mask
        polygon_mask = np.zeros(
            (height, width),
            dtype=np.uint8
        )

        shifted_polygon = np.array(
            [
                [x - x1, y - y1]
                for x, y in polygon
            ],
            dtype=np.int32
        )

        cv2.fillPoly(
            polygon_mask,
            [shifted_polygon],
            255
        )

        intersection = cv2.bitwise_and(
            vehicle_mask,
            polygon_mask
        )

        intersection_area = cv2.countNonZero(
            intersection
        )

        vehicle_area = cv2.countNonZero(
            vehicle_mask
        )

        if vehicle_area == 0:
            return 0

        return intersection_area / vehicle_area


    # ---------------------------------
    # Process frame
    # ---------------------------------

    def process_frame(
        self,
        frame,
        parking_spaces,
        confidence=0.25
    ):

        results = self.model.track(
            frame,

            # Geo-trax was trained at 1920 resolution
            imgsz=1920,

            persist=True,

            conf=confidence,

            classes=VEHICLE_CLASSES,

            verbose=False
        )

        vehicles = []


        # ---------------------------------
        # Extract detected vehicles
        # ---------------------------------

        if results and results[0].boxes:

            boxes = results[0].boxes

            for i in range(len(boxes)):

                xyxy = (
                    boxes.xyxy[i]
                    .cpu()
                    .numpy()
                    .astype(int)
                )

                x1, y1, x2, y2 = xyxy

                confidence_score = float(
                    boxes.conf[i]
                )

                class_id = int(
                    boxes.cls[i]
                )


                # Tracker ID
                if boxes.id is not None:

                    track_id = int(
                        boxes.id[i]
                    )

                else:

                    track_id = -1


                # Vehicle center
                center_x = int(
                    (x1 + x2) / 2
                )

                center_y = int(
                    (y1 + y2) / 2
                )


                vehicles.append({

                    "box": (
                        x1,
                        y1,
                        x2,
                        y2
                    ),

                    "center": (
                        center_x,
                        center_y
                    ),

                    "confidence": confidence_score,

                    "class_id": class_id,

                    "track_id": track_id

                })


        # ---------------------------------
        # Determine occupied parking spaces
        # ---------------------------------

        occupied_spaces = []


        for space_id, polygon in parking_spaces.items():

            occupied = False


            for vehicle in vehicles:

                overlap = self.calculate_overlap(
                    vehicle["box"],
                    polygon
                )


                center_inside = self.point_inside_polygon(
                    vehicle["center"],
                    polygon
                )


                # Vehicle occupies space if:
                #
                # 20%+ of vehicle overlaps polygon
                # OR
                # vehicle center is inside polygon

                if overlap >= 0.20 or center_inside:

                    occupied = True

                    break


            if occupied:

                occupied_spaces.append(
                    space_id
                )


        return vehicles, occupied_spaces


    # ---------------------------------
    # Draw parking monitor
    # ---------------------------------

    def draw_monitor(
        self,
        frame,
        parking_spaces,
        occupied_spaces,
        vehicles
    ):

        output = frame.copy()


        # ---------------------------------
        # Draw parking spaces
        # ---------------------------------

        for space_id, polygon in parking_spaces.items():

            polygon_np = np.array(
                polygon,
                dtype=np.int32
            )


            if space_id in occupied_spaces:

                color = (0, 0, 255)

                status = "OCCUPIED"

            else:

                color = (0, 200, 0)

                status = "FREE"


            cv2.polylines(
                output,
                [polygon_np],
                True,
                color,
                2
            )


            # Polygon center
            M = cv2.moments(
                polygon_np
            )


            if M["m00"] != 0:

                cx = int(
                    M["m10"] /
                    M["m00"]
                )

                cy = int(
                    M["m01"] /
                    M["m00"]
                )


                cv2.putText(
                    output,

                    f"{space_id}: {status}",

                    (
                        cx - 40,
                        cy
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.45,

                    color,

                    2
                )


        # ---------------------------------
        # Draw detected vehicles
        # ---------------------------------

        for vehicle in vehicles:

            x1, y1, x2, y2 = vehicle["box"]

            track_id = vehicle["track_id"]

            confidence = vehicle["confidence"]


            cv2.rectangle(
                output,

                (x1, y1),

                (x2, y2),

                (255, 200, 0),

                2
            )


            cv2.putText(
                output,

                f"Vehicle {track_id} {confidence:.2f}",

                (
                    x1,
                    max(y1 - 8, 20)
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.5,

                (255, 200, 0),

                2
            )


        return output