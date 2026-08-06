from ultralytics import YOLO
import glob

model = YOLO("yolov8n.pt")

# grab first 10 test images
image_paths = glob.glob("Drone-detection-4/test/images/*.jpg")[:10]

results = model(image_paths)

for i, r in enumerate(results):
    r.save(filename=f"drone_output_{i}.jpg")
    print(image_paths[i], "->", r.boxes.cls, r.boxes.conf)