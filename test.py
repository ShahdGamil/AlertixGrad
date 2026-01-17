from ultralytics import YOLO

# load trained model
model = YOLO("C:\\Users\\shaho\\OneDrive - Nile University\\Desktop\\dataset_grad\\runs\\detect\\train5\\weights\\best.pt")

# run prediction
results = model.predict(
    source="test.jpg",   # path to your image
    conf=0.5,            # filter weak detections
    iou=0.5,
    save=True            # saves output image
)

print("Done")
