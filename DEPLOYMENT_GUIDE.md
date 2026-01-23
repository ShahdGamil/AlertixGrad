# YOLOv8 Retail Theft Detection - Deployment & Inference Guide

## 🎯 Quick Start

Once training is complete, use the model like this:

```python
from ultralytics import YOLO

# Load the trained model
model = YOLO('runs/detect/retail_theft_final/weights/best.pt')

# Run inference on an image
results = model.predict('store_image.jpg', conf=0.25)

# Process results
for result in results:
    print(f"Found {len(result.boxes)} objects")
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        print(f"  Class: {class_id}, Confidence: {confidence:.2%}")
```

---

## 📋 Complete Class Reference

| ID | Class Name | Description | Example |
|----|-----------|-------------|---------|
| 0 | Customer-Bagpack | Person wearing backpack (suspicious) | Person with full backpack in store |
| 1 | Product | Individual product/item | Bottle, box, clothing |
| 2 | Product-Picked | Item removed from shelf | Hand taking item off shelf |
| 3 | Shopping-Cart | Cart (legitimate activity) | Shopping cart with items |
| 4 | normal | Normal customer behavior | Person browsing, paying |
| 5 | **theft** | **Theft-related activity** | **Taking item without payment** |

---

## 🚨 Theft Detection Example

```python
from ultralytics import YOLO

model = YOLO('runs/detect/retail_theft_final/weights/best.pt')
results = model.predict('surveillance_footage.jpg', conf=0.25)

for result in results:
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        
        if class_id == 5:  # Theft class
            print(f"🚨 THEFT DETECTED! Confidence: {confidence:.1%}")
            print(f"   Location: {box.xyxy[0]}")
            
            # Trigger alert/notification
            send_alert(f"Potential theft detected: {confidence:.1%}")
```

---

## 📹 Video Processing

### Process Entire Video File
```python
from ultralytics import YOLO
from pathlib import Path

model = YOLO('runs/detect/retail_theft_final/weights/best.pt')

# Process video
results = model.predict(
    source='security_video.mp4',
    conf=0.25,
    save=True,           # Save annotated output
    save_txt=True,       # Save detections to txt files
    device='cpu'         # Use CPU
)

print(f"Results saved to: runs/detect/predict/")
```

### Real-Time Camera Stream
```python
import cv2
from ultralytics import YOLO

model = YOLO('runs/detect/retail_theft_final/weights/best.pt')

# Camera source (0 = default webcam)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Run inference
    results = model(frame, conf=0.25, verbose=False)
    
    # Annotate frame
    annotated = results[0].plot()
    
    # Check for theft
    for box in results[0].boxes:
        if int(box.cls[0]) == 5:
            print("🚨 THEFT ALERT!")
            # Play sound, send notification, etc.
    
    # Display
    cv2.imshow('Theft Detection', annotated)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 🎬 Output Processing

### Access Detection Results
```python
from ultralytics import YOLO

model = YOLO('best.pt')
results = model.predict('image.jpg', conf=0.25)

for result in results:
    # Bounding boxes
    boxes = result.boxes  # ultralytics.yolo.results.Boxes object
    
    for box in boxes:
        # Class information
        class_id = int(box.cls[0])        # Class ID
        class_name = model.names[class_id]  # Class name
        confidence = float(box.conf[0])   # Confidence score
        
        # Coordinates (different formats available)
        xyxy = box.xyxy[0]                # [x1, y1, x2, y2] format
        xywh = box.xywh[0]                # [x_center, y_center, w, h] format
        
        print(f"{class_name}: {confidence:.2%} at {xyxy}")
```

### Batch Processing Multiple Images
```python
from ultralytics import YOLO
from pathlib import Path

model = YOLO('best.pt')

# Process all images in directory
image_dir = Path('retail_images/')
results = model.predict(source=list(image_dir.glob('*.jpg')), conf=0.25)

# Analyze results
theft_count = 0
for result in results:
    for box in result.boxes:
        if int(box.cls[0]) == 5:
            theft_count += 1

print(f"Total theft detections: {theft_count}")
```

### Export Detections to JSON
```python
import json
from ultralytics import YOLO

model = YOLO('best.pt')
results = model.predict('image.jpg', conf=0.25)

detections = []
for result in results:
    for box in result.boxes:
        detection = {
            'class_id': int(box.cls[0]),
            'class_name': model.names[int(box.cls[0])],
            'confidence': float(box.conf[0]),
            'bbox': box.xyxy[0].tolist(),
            'area_pixels': float(box.xyxy[0][2] - box.xyxy[0][0]) * 
                          float(box.xyxy[0][3] - box.xyxy[0][1])
        }
        detections.append(detection)

# Save to JSON
with open('detections.json', 'w') as f:
    json.dump(detections, f, indent=2)
```

---

## ⚙️ Confidence Threshold Tuning

### Recommended Settings by Use Case

```python
model = YOLO('best.pt')

# Scenario 1: Maximum Security (catch all thefts, accept false alerts)
results = model.predict(source='image.jpg', conf=0.15)

# Scenario 2: Balanced (Recommended for retail)
results = model.predict(source='image.jpg', conf=0.25)

# Scenario 3: High Precision (fewer alerts, might miss some thefts)
results = model.predict(source='image.jpg', conf=0.35)

# Scenario 4: Very High Precision (only confident detections)
results = model.predict(source='image.jpg', conf=0.50)
```

### Class-Specific Thresholding
```python
from ultralytics import YOLO

model = YOLO('best.pt')
results = model.predict('image.jpg', conf=0.25)

for result in results:
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        
        # Stricter requirements for theft alerts
        if class_id == 5 and confidence >= 0.30:
            print("HIGH CONFIDENCE THEFT ALERT!")
        
        # More lenient for other detections
        elif confidence >= 0.25:
            print(f"Detection: {class_id}")
```

---

## 🔍 Model Information

### Get Model Stats
```python
from ultralytics import YOLO

model = YOLO('best.pt')

# Print model information
print(model.info())

# Get class names
print(model.names)  
# Output: {0: 'Customer-Bagpack', 1: 'Product', ...}

# Get model size
print(f"Model size: {model.model_size} MB")
```

### Inference Speed Benchmark
```python
import time
from ultralytics import YOLO

model = YOLO('best.pt')

# Warmup
_ = model.predict('dummy.jpg', verbose=False)

# Benchmark
start = time.time()
for _ in range(10):
    results = model.predict('image.jpg', verbose=False)
avg_time = (time.time() - start) / 10

print(f"Average inference time: {avg_time*1000:.1f} ms")
print(f"FPS: {1/avg_time:.1f}")
```

---

## 💾 Model Export Formats

### Export to ONNX (Universal Format)
```python
from ultralytics import YOLO

model = YOLO('best.pt')
onnx_model = model.export(format='onnx')

# Use with ONNX Runtime
import onnxruntime as ort
session = ort.InferenceSession('best.onnx')
```

### Export to TensorFlow
```python
model = YOLO('best.pt')
tf_model = model.export(format='tf')
# Can use with TFLite for mobile
```

### Export to OpenVINO (Intel Edge)
```python
model = YOLO('best.pt')
openvino_model = model.export(format='openvino')
```

### Export to TorchScript
```python
model = YOLO('best.pt')
torchscript_model = model.export(format='torchscript')
```

---

## 🐳 Docker Deployment

### Simple Docker Container
```dockerfile
FROM python:3.11

WORKDIR /app

# Install dependencies
RUN pip install ultralytics opencv-python

# Copy model
COPY best.pt .

# Inference script
COPY inference.py .

ENTRYPOINT ["python", "inference.py"]
```

### Run Container
```bash
docker build -t theft-detector .
docker run --volume /path/to/images:/input theft-detector /input/image.jpg
```

---

## 📊 Monitoring & Logging

### Log All Detections
```python
import csv
from datetime import datetime
from ultralytics import YOLO

model = YOLO('best.pt')

class_names = model.names

with open('theft_log.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'class', 'confidence', 'x1', 'y1', 'x2', 'y2'])
    
    results = model.predict('video.mp4', conf=0.25)
    for result in results:
        for box in result.boxes:
            writer.writerow([
                datetime.now().isoformat(),
                class_names[int(box.cls[0])],
                float(box.conf[0]),
                *box.xyxy[0].tolist()
            ])
```

### Real-Time Monitoring Dashboard (with Streamlit)
```python
import streamlit as st
from ultralytics import YOLO
import cv2

st.title("Retail Theft Detection System")

model = YOLO('best.pt')

# Upload image
uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    # Run inference
    results = model.predict(uploaded_file, conf=0.25)
    
    # Display results
    annotated = results[0].plot()
    st.image(annotated)
    
    # Show detections
    for box in results[0].boxes:
        col1, col2 = st.columns(2)
        col1.write(f"Class: {model.names[int(box.cls[0])]}")
        col2.write(f"Confidence: {float(box.conf[0]):.2%}")
```

---

## ⚡ Optimization for Production

### Reduce Model Size (Quantization)
```python
# Note: Not directly supported in YOLO, but can export to ONNX
# then quantize with ONNX Runtime
model = YOLO('best.pt')
onnx_model = model.export(format='onnx')
```

### Use Mixed Precision (if GPU available later)
```python
model = YOLO('best.pt')
results = model.predict('image.jpg', conf=0.25, half=True)
```

### Optimize for CPU Inference
```python
# Use ONNX with ONNX Runtime for faster CPU inference
import onnxruntime as ort
import numpy as np

session = ort.InferenceSession('best.onnx', 
                              providers=['CPUExecutionProvider'])
```

---

## 🔧 Troubleshooting

### Model Not Loading
```python
# Check if model exists
from pathlib import Path
model_path = Path('runs/detect/retail_theft_final/weights/best.pt')
assert model_path.exists(), f"Model not found at {model_path}"

from ultralytics import YOLO
model = YOLO(str(model_path))
```

### Low Inference Speed
```python
# If running on CPU, this is normal
# Options:
# 1. Reduce image size
results = model.predict('image.jpg', imgsz=416)

# 2. Reduce batch size
results = model.predict('image.jpg', batch=1)

# 3. Use ONNX Runtime
# (faster CPU inference than PyTorch)
```

### Out of Memory
```python
# Reduce batch size for video
results = model.predict(
    'video.mp4',
    batch=1,
    verbose=False
)
```

---

## 📞 Support

For issues or questions:
1. Check YOLOv8 documentation: https://docs.ultralytics.com
2. GitHub Issues: https://github.com/ultralytics/ultralytics/issues
3. Community Discussion: https://github.com/ultralytics/ultralytics/discussions

---

**Last Updated**: 2026-01-18  
**Model Version**: YOLOv8 Nano  
**Dataset**: Retail Theft Detection (2,578 images)
