from ultralytics import YOLO

model = YOLO("yolov8n.pt")

# put your own image filenames here
my_images = ["image_1.png", "image_2.png","image_3.png","image_4.png"]

results = model(my_images)

for i, r in enumerate(results):
    r.save(filename=f"my_output_{i}.jpg")
    print(my_images[i], r.boxes)