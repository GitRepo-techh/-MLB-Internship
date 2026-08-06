from ultralytics import YOLO

# Load a pretrained YOLOv8 model (nano version - smallest/fastest)
model = YOLO("yolov8n.pt")  # auto-downloads on first run (~6MB)

# Run inference directly on an image URL (ultralytics handles the download)
results = model("https://ultralytics.com/images/bus.jpg")

# Save and inspect results
for r in results:
    r.save(filename="output_single.jpg")