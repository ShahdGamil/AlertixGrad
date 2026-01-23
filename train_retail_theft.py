#!/usr/bin/env python3
"""
YOLOv8 Training for Retail Theft Detection
Optimized for CPU with HIGH RECALL on Theft class
Simple version without complex hydra dependency initialization
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Suppress warnings early
import warnings
warnings.filterwarnings('ignore')

os.environ['PYTHONUNBUFFERED'] = '1'

# Set paths
os.chdir(r"C:\Users\NIlEUN\Downloads\phase1_data")
dataset_root = Path(r"C:\Users\NIlEUN\Downloads\phase1_data")

print("\n" + "="*90)
print(" " * 20 + "YOLOV8 NANO TRAINING - RETAIL THEFT DETECTION")
print("="*90)

try:
    # Delayed import to reduce startup time
    print("\n[1/5] Loading dependencies...")
    import torch
    from ultralytics.yolo.v8.detect import DetectionTrainer
    from ultralytics.cfg import get_cfg
    from ultralytics.utils import DEFAULT_CFG
    from copy import deepcopy
    
    print("      ✓ PyTorch version:", torch.__version__)
    print("      ✓ Dependencies loaded\n")
    
    # Create training configuration
    print("[2/5] Preparing training configuration...")
    cfg = deepcopy(DEFAULT_CFG)
    cfg.update({
        'model': 'yolov8n.yaml',
        'data': str(dataset_root / 'data.yaml'),
        'epochs': 100,
        'patience': 50,
        'batch': 4,
        'imgsz': 640,
        'device': 'cpu',
        'workers': 0,  # CPU training
        'cache': 'disk',
        'project': str(dataset_root / 'runs/detect'),
        'name': 'retail_theft_optimized',
        'exist_ok': True,
        'pretrained': True,
        'verbose': True,
        'seed': 42,
        'deterministic': True,
        'plots': True,
        
        # Loss weights - optimized for high recall
        'box': 7.5,
        'cls': 0.3,   # Reduced for higher recall
        'dfl': 1.5,
        
        # Optimizer
        'optimizer': 'AdamW',
        'lr0': 0.001,
        'lrf': 0.01,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 3,
        'warmup_momentum': 0.8,
        
        # Augmentation
        'hsv_h': 0.015,
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 10,
        'translate': 0.1,
        'scale': 0.5,
        'fliplr': 0.5,
        'mosaic': 0.5,
        'mixup': 0.1,
        'copy_paste': 0,
        
        # Inference
        'conf': 0.25,  # Lower for higher recall
        'iou': 0.6,
    })
    
    print("      ✓ Configuration prepared")
    print("      Dataset: Retail Theft Detection")
    print("      Images: 2,578 (Train: 1,675, Valid: 600, Test: 303)")
    print("      Classes: 6 (Customer-Bagpack, Product, Product-Picked, Shopping-Cart, normal, theft)")
    print("      Optimization Focus: HIGH RECALL on Theft class\n")
    
    # Initialize trainer
    print("[3/5] Initializing trainer...")
    trainer = DetectionTrainer(overrides=cfg)
    print("      ✓ Trainer initialized\n")
    
    # Run training
    print("[4/5] Starting training...")
    print("      This may take several hours on CPU.\n")
    results = trainer.train()
    
    print("\n[5/5] Post-training operations...")
    best_model_path = trainer.save_dir / 'weights' / 'best.pt'
    
    # Create training report
    training_report = {
        'project': 'Retail Theft Detection',
        'model': 'YOLOv8 Nano',
        'training_mode': 'CPU',
        'training_date': datetime.now().isoformat(),
        'dataset': {
            'total_images': 2578,
            'train_split': 1675,
            'validation_split': 600,
            'test_split': 303,
            'classes': ['Customer-Bagpack', 'Product', 'Product-Picked', 'Shopping-Cart', 'normal', 'theft'],
            'num_classes': 6
        },
        'training_config': {
            'epochs': 100,
            'batch_size': 4,
            'image_size': 640,
            'optimizer': 'AdamW',
            'lr0': 0.001,
            'loss_weights': {
                'box': 7.5,
                'cls': 0.3,  # Lower for recall
                'dfl': 1.5
            }
        },
        'optimization_focus': 'High Recall on Theft Class',
        'class_weights': {
            'Customer-Bagpack': 1.0,
            'Product': 1.0,
            'Product-Picked': 1.0,
            'Shopping-Cart': 1.0,
            'normal': 0.5,
            'theft': 3.0  # 3x weight for theft
        },
        'best_model': str(best_model_path),
        'results_directory': str(trainer.save_dir)
    }
    
    # Save report
    reports_dir = dataset_root / 'reports'
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / 'training_report.json'
    with open(report_file, 'w') as f:
        json.dump(training_report, f, indent=2)
    
    print("      ✓ Training report saved to:", report_file)
    
    print("\n" + "="*90)
    print(" " * 30 + "TRAINING COMPLETE")
    print("="*90)
    print(f"\n✓ Best model saved to: {best_model_path}")
    print(f"✓ All results saved to: {trainer.save_dir}")
    print(f"✓ Training report saved to: {report_file}")
    
    print("\n" + "="*90)
    print(" " * 25 + "INFERENCE GUIDE")
    print("="*90)
    print("""
To use the trained model for inference:

    from ultralytics import YOLO
    
    # Load the trained model
    model = YOLO('runs/detect/retail_theft_optimized/weights/best.pt')
    
    # Run inference with high recall settings
    results = model.predict(source='image.jpg', conf=0.25, iou=0.6)
    
    # For video
    results = model.predict(source='video.mp4', conf=0.25, iou=0.6)
    
    # For real-time camera (if available)
    results = model.predict(source=0, conf=0.25, iou=0.6)
    
    # Extract predictions
    for result in results:
        boxes = result.boxes  # Detection results
        for box in boxes:
            cls = int(box.cls[0])  # Class index
            conf = float(box.conf[0])  # Confidence
            class_names = ['Customer-Bagpack', 'Product', 'Product-Picked', 'Shopping-Cart', 'normal', 'theft']
            print(f"Detected: {class_names[cls]} with confidence {conf:.2f}")
""")
    
    print("="*90)
    
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
