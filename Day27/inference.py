from ultralytics import YOLO

# 1. Load your trained model
model = YOLO("C:/VsCode/-MLB-Internship/runs/detect/train-7/weights/best.pt")

# 2. Run inference on your test folder
results = model.predict(
    source="test_samples",
    conf=0.25,
    save=True
)

# 3. Print detections with confidence scores
for result in results:

    print(f"\nImage: {result.path}")

    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        class_name = model.names[cls_id]
        print(f"  Detected: {class_name} and confidence: {conf:.2f}")