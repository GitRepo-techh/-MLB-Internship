from datetime import datetime


def calculate_statistics(
    total_spaces,
    occupied_spaces
):

    available_spaces = (
        total_spaces - occupied_spaces
    )

    if total_spaces > 0:

        occupancy_percentage = (
            occupied_spaces /
            total_spaces
        ) * 100

    else:

        occupancy_percentage = 0

    if occupancy_percentage < 40:

        utilization = "LOW"

    elif occupancy_percentage < 75:

        utilization = "MEDIUM"

    else:

        utilization = "HIGH"

    return {
        "total": total_spaces,
        "occupied": occupied_spaces,
        "available": available_spaces,
        "percentage": occupancy_percentage,
        "utilization": utilization
    }


def draw_analytics_panel(
    frame,
    statistics,
    frame_number,
    fps
):

    import cv2

    height, width = frame.shape[:2]

    panel_width = 330

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (
            width - panel_width,
            0
        ),
        (
            width,
            250
        ),
        (20, 20, 20),
        -1
    )

    # Transparency
    frame = cv2.addWeighted(
        overlay,
        0.80,
        frame,
        0.20,
        0
    )

    x = width - panel_width + 20

    cv2.putText(
        frame,
        "PARKING ANALYTICS",
        (x, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Total: {statistics['total']}",
        (x, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Occupied: {statistics['occupied']}",
        (x, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (110, 100, 255),
        2
    )

    cv2.putText(
        frame,
        f"Available: {statistics['available']}",
        (x, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 220, 100),
        2
    )

    cv2.putText(
        frame,
        f"Occupancy: {statistics['percentage']:.1f}%",
        (x, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 25, 255),
        2
    )

    cv2.putText(
        frame,
        f"Utilization: {statistics['utilization']}",
        (x, 215),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Frame: {frame_number}",
        (20, height - 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cv2.putText(
        frame,
        timestamp,
        (20, height - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        2
    )

    return frame