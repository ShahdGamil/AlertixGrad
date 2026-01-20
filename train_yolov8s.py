#!/usr/bin/env python3
"""
YOLOv8s Training Script for Retail Theft Detection
Generated: 2026-01-19T03:16:16.679092

Usage:
    python train_yolov8s.py
"""

import torch
from ultralytics import YOLO
from pathlib import Path

# Verify GPU
print("="*60)
print("GPU VERIFICATION")
print("="*60)
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA: {torch.version.cuda}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("[WARNING] No GPU detected! Training on CPU.")
print("="*60)

# Configuration
DATA_YAML = r"c:\Users\shaho\OneDrive - Nile University\Desktop\AletrixGrad\configs\data.yaml"
MODEL = "yolov8s.pt"
EPOCHS = 100
BATCH_SIZE = 2
IMG_SIZE = 640
DEVICE = 0 if torch.cuda.is_available() else "cpu"

def main():
    # Load model (pretrained on COCO)
    print("\nLoading YOLOv8s model...")
    model = YOLO(MODEL)
    
    # Train
    print("\nStarting training...")
    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        batch=BATCH_SIZE,
        imgsz=IMG_SIZE,
        device=DEVICE,
        
        # Optimizer
        optimizer="AdamW",
        lr0=0.01,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        
        # Loss
        box=7.5,
        cls=0.5,
        dfl=1.5,
        
        # Augmentation (retail surveillance optimized)
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=0.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.0,
        
        # Hardware
        workers=8,
        cache=True,
        amp=True,
        
        # Output
        project=r"c:\Users\shaho\OneDrive - Nile University\Desktop\AletrixGrad\runs",
        name="retail_theft_yolov8s",
        exist_ok=True,
        pretrained=True,
        verbose=True,
        seed=42,
        
        # Validation
        val=True,
        plots=True,
        save=True,
        save_period=10,
        patience=30,
    )
    
    print("\nTraining complete!")
    print(f"Results saved to: {results.save_dir}")
    
    return results

if __name__ == "__main__":
    main()
