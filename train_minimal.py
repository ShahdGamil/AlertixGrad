#!/usr/bin/env python3
import os
os.chdir(r"C:\Users\NIlEUN\Downloads\phase1_data")
os.environ['PYTHONUNBUFFERED'] = '1'

import warnings; warnings.filterwarnings('ignore')
import sys

def main():
    print("Starting YOLOv8 Nano Training")
    print("Dataset: Retail Theft Detection")
    print("Mode: CPU")

    from ultralytics import YOLO

    print("Loading model...")
    model = YOLO("yolov8n.pt")

    print("Starting training...")
    results = model.train(
        data=r"C:\Users\NIlEUN\Downloads\phase1_data\data.yaml",
        epochs=100, imgsz=640, batch=4, patience=50, device='cpu',
        optimizer='AdamW', lr0=0.001, lrf=0.01, momentum=0.937,
        weight_decay=0.0005, warmup_epochs=3, box=7.5, cls=0.3, dfl=1.5,
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, degrees=10, translate=0.1,
        scale=0.5, fliplr=0.5, mosaic=0.5, mixup=0.1,
        project=r"C:\Users\NIlEUN\Downloads\phase1_data\runs\detect",
        name='retail_theft_final', exist_ok=True, verbose=False, save=True,
        plots=True, val=True, seed=42, workers=0
    )

    print("Training completed!")
    print(f"Model saved: {results.save_dir}/weights/best.pt")

if __name__ == '__main__':
    main()
