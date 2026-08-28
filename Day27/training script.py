from ultralytics import YOLO

model = YOLO("yolov8n.pt")
train = model.train(data = "C:/useful trash/helmat dataset/data.yaml", epochs = 23, batch = 8, imgsz = 640, device = "cpu", project="runs/detect", name="helmet_detector", exist_ok=True)
