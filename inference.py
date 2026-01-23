#!/usr/bin/env python3
"""
YOLOv8 Inference Script for Retail Theft Detection

Usage:
    python inference.py --source path/to/image_or_video
    python inference.py --source 0  # webcam
"""

import argparse
from ultralytics import YOLO
import cv2
import os

# Class names
CLASS_NAMES = ['Customer-Bagpack', 'Product', 'Product-Picked', 'Shopping-Cart', 'normal', 'theft']

# Class colors (BGR)
CLASS_COLORS = {
    0: (0, 0, 255),      # Customer-Bagpack - Red
    1: (0, 255, 0),      # Product - Green
    2: (255, 0, 0),      # Product-Picked - Blue
    3: (255, 255, 0),    # Shopping-Cart - Cyan
    4: (255, 0, 255),    # normal - Magenta
    5: (0, 165, 255),    # theft - Orange (highlight)
}

def run_inference(
    model_path: str,
    source: str,
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
    save_output: bool = True,
    show: bool = True
):
    """Run inference on source."""
    # Load model
    model = YOLO(model_path)

    # Run inference
    results = model.predict(
        source=source,
        conf=conf_threshold,
        iou=iou_threshold,
        save=save_output,
        show=show,
        stream=True  # For videos/webcam
    )

    # Process results
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else f"Class_{cls_id}"

                # Alert for theft detection
                if cls_id == 5:  # Theft class
                    print(f"[ALERT] THEFT DETECTED! Confidence: {conf:.2f}")

                print(f"Detected: {class_name} ({conf:.2f})")

    print("\nInference complete!")


def main():
    parser = argparse.ArgumentParser(description='YOLOv8 Retail Theft Detection Inference')
    parser.add_argument('--model', type=str, default='runs/detect/retail_theft/weights/best.pt',
                        help='Path to trained model')
    parser.add_argument('--source', type=str, required=True,
                        help='Source (image, video, or camera index)')
    parser.add_argument('--conf', type=float, default=0.25,
                        help='Confidence threshold')
    parser.add_argument('--iou', type=float, default=0.45,
                        help='IoU threshold for NMS')
    parser.add_argument('--save', action='store_true',
                        help='Save output')
    parser.add_argument('--no-show', action='store_true',
                        help='Do not display output')

    args = parser.parse_args()

    run_inference(
        model_path=args.model,
        source=args.source,
        conf_threshold=args.conf,
        iou_threshold=args.iou,
        save_output=args.save,
        show=not args.no_show
    )


if __name__ == '__main__':
    main()
