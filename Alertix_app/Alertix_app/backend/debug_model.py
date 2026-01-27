"""
Debug script to test YOLO model directly
Run this with a theft image to see what the model detects
"""
import sys
import os
from ultralytics import YOLO
import cv2

# Load the model being used by backend
MODEL_PATH = "best (4).pt"

print("=" * 60)
print("YOLO Model Debug Script")
print("=" * 60)

# Load model
print(f"\nLoading model: {MODEL_PATH}")
model = YOLO(MODEL_PATH)

# Print model info
print(f"\nModel classes: {model.names}")
print(f"Number of classes: {len(model.names)}")

# Check if an image path was provided
if len(sys.argv) > 1:
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)
    
    print(f"\nTesting with image: {image_path}")
    
    # Load image
    image = cv2.imread(image_path)
    print(f"Image shape: {image.shape}")
    
    # Run inference with LOW threshold to see all detections
    print("\n" + "=" * 60)
    print("Running inference with CONF=0.10 (low threshold to see all)")
    print("=" * 60)
    
    results = model.predict(
        image,
        imgsz=640,
        conf=0.10,  # Very low to see ALL detections
        iou=0.5,
        verbose=True
    )
    
    # Parse results
    if len(results) > 0:
        result = results[0]
        
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy().astype(int)
            
            print(f"\n{'='*60}")
            print(f"FOUND {len(boxes)} DETECTIONS:")
            print(f"{'='*60}")
            
            for i, (box, conf, cls_id) in enumerate(zip(boxes, confidences, classes)):
                cls_name = model.names.get(int(cls_id), f"Unknown-{cls_id}")
                is_theft = "*** THEFT ***" if cls_id == 5 else ""
                is_normal = "(normal)" if cls_id == 4 else ""
                
                print(f"\n  Detection {i+1}:")
                print(f"    Class: {cls_name} (ID: {cls_id}) {is_theft} {is_normal}")
                print(f"    Confidence: {conf:.4f} ({conf*100:.1f}%)")
                print(f"    Box: [{box[0]:.0f}, {box[1]:.0f}, {box[2]:.0f}, {box[3]:.0f}]")
                
                # Threshold check
                if conf >= 0.25:
                    print(f"    >> Would be detected with conf=0.25 threshold")
                else:
                    print(f"    >> TOO LOW for conf=0.25 threshold")
            
            # Summary
            theft_detections = [c for c in classes if c == 5]
            normal_detections = [c for c in classes if c == 4]
            
            print(f"\n{'='*60}")
            print(f"SUMMARY:")
            print(f"  - Total detections: {len(boxes)}")
            print(f"  - Theft detections (class 5): {len(theft_detections)}")
            print(f"  - Normal detections (class 4): {len(normal_detections)}")
            print(f"  - Other detections: {len(boxes) - len(theft_detections) - len(normal_detections)}")
            print(f"{'='*60}")
            
            # Save annotated image
            output_path = "debug_detection_output.jpg"
            result.save(output_path)
            print(f"\nSaved annotated image to: {output_path}")
            
        else:
            print("\n>>> NO DETECTIONS FOUND AT ALL <<<")
            print("This could mean:")
            print("  1. The image doesn't contain any recognizable objects")
            print("  2. The model wasn't trained on this type of image")
            print("  3. The image quality/resolution is too different from training data")
    else:
        print("No results returned from model")
else:
    print("\nUsage: python debug_model.py <path_to_image>")
    print("Example: python debug_model.py test_theft.jpg")
    print("\nNote: Place a theft image in this folder and run:")
    print("  python debug_model.py <your_image.jpg>")
