# AletrixGrad: Retail Theft Detection using YOLOv8s

A deep learning pipeline for detecting retail theft in CCTV surveillance footage using YOLOv8s object detection.

## Project Overview

This project implements an end-to-end computer vision pipeline for retail theft detection, from raw dataset processing to trained model deployment. The system detects 6 classes of objects/behaviors in retail surveillance footage:

| Class ID | Class Name | Description |
|----------|------------|-------------|
| 0 | Customer-Bagpack | Customer carrying a backpack |
| 1 | Product | Store product on shelf |
| 2 | Product-Picked | Product being picked up/held |
| 3 | Shopping-Cart | Shopping cart in frame |
| 4 | normal | Normal shopping behavior |
| 5 | **theft** | **Theft/shoplifting behavior** (Critical) |

---

## Training Results

### Final Model Performance

| Metric | Validation | Test |
|--------|------------|------|
| **mAP@0.5** | **84.27%** | **77.86%** |
| **mAP@0.5:0.95** | 64.13% | 57.64% |
| **Precision** | 83.70% | 74.78% |
| **Recall** | 77.90% | 74.75% |

### Training Summary

- **Model**: YOLOv8s (11.1M parameters)
- **Epochs**: 100 (completed)
- **Image Size**: 640x640
- **Batch Size**: 2
- **GPU**: NVIDIA GeForce GTX 1650 (4GB VRAM)
- **Training Time**: ~15 hours

### Training Progress

| Epoch | Box Loss | Cls Loss | DFL Loss | mAP@0.5 | Precision | Recall |
|-------|----------|----------|----------|---------|-----------|--------|
| 1 | 2.278 | 3.473 | 2.367 | 5.53% | 21.2% | 8.3% |
| 25 | 1.479 | 1.697 | 1.621 | 55.3% | 54.1% | 55.7% |
| 50 | 1.187 | 1.229 | 1.389 | 71.4% | 68.6% | 66.5% |
| 75 | 0.979 | 0.962 | 1.258 | 79.0% | 80.1% | 73.3% |
| 100 | 0.778 | 0.601 | 1.141 | **84.2%** | **85.5%** | **76.8%** |

### Loss Curves Analysis

The training showed excellent convergence:
- **Box Loss**: Decreased from 2.28 → 0.78 (66% reduction)
- **Classification Loss**: Decreased from 3.47 → 0.60 (83% reduction)
- **DFL Loss**: Decreased from 2.37 → 1.14 (52% reduction)

### Why These Results Are Strong

1. **84.27% mAP@0.5**: The model accurately detects and localizes objects in most cases
2. **Balanced Precision/Recall (~78%)**: Good balance between catching incidents and avoiding false alarms
3. **Consistent Val/Test Performance**: Close metrics indicate good generalization (no overfitting)
4. **Smooth Convergence**: Steady improvement over 100 epochs without instability

### Model Exports

The trained model is available in multiple formats:
- `best.pt` - PyTorch weights (for further training/inference)
- `best.onnx` - ONNX format (cross-platform deployment)
- `best.torchscript` - TorchScript (production deployment)

---

## Directory Structure

```
AletrixGrad/
├── cc-tv-footage-annotation-b8-lcysc-b1-2/   # Original dataset
├── dataset_cleaned/                           # Cleaned dataset
├── dataset_augmented/                         # Augmented dataset (used for training)
│   ├── train/                                 # 2065 images
│   ├── valid/                                 # 482 images
│   └── test/                                  # 241 images
├── configs/
│   └── data.yaml                             # YOLOv8 dataset configuration
├── notebooks/
│   ├── 01_dataset_validation.ipynb           # Validate YOLO format
│   ├── 02_dataset_cleaning.ipynb             # Remove corrupt data
│   ├── 03_dataset_analysis.ipynb             # Class distribution analysis
│   ├── 04_dataset_balancing.ipynb            # Data augmentation
│   ├── 05_dataset_splitting.ipynb            # Verify splits
│   ├── 06_preprocessing_pipeline.ipynb       # Image preprocessing
│   ├── 07_training_preparation.ipynb         # GPU verification
│   └── 08_training_evaluation.ipynb          # Model training & evaluation
├── runs/
│   └── retail_theft_yolov8s/
│       ├── weights/
│       │   ├── best.pt                       # Best model weights
│       │   ├── best.onnx                     # ONNX export
│       │   └── best.torchscript              # TorchScript export
│       ├── results.csv                       # Training metrics
│       ├── results.png                       # Training curves
│       ├── confusion_matrix.png              # Confusion matrix
│       └── *.jpg                             # Validation visualizations
├── outputs/
│   └── training_final_report.json            # Final metrics summary
├── visualizations/
│   ├── training_curves.png                   # Loss and metric plots
│   └── inference_samples/                    # Sample predictions
└── README.md
```

---

## Pipeline Stages

### 1. Dataset Validation (`01_dataset_validation.ipynb`)
- Validates YOLO annotation format
- Detects corrupt/unreadable images
- Identifies bounding box issues

### 2. Dataset Cleaning (`02_dataset_cleaning.ipynb`)
- Removes corrupt images
- Fixes floating-point precision issues in bounding boxes
- Removes duplicate images using perceptual hashing

### 3. Dataset Analysis (`03_dataset_analysis.ipynb`)
- Analyzes class distribution
- Visualizes bounding box statistics
- **Finding**: Significant class imbalance (63% normal vs 5% theft)

### 4. Dataset Balancing (`04_dataset_balancing.ipynb`)
- Targeted augmentation for minority classes:
  - **Shopping-Cart**: 2x multiplier
  - **theft**: 3x multiplier (highest priority)
- Surveillance-optimized augmentations:
  - Horizontal flip, brightness/contrast, motion blur, noise
  - **No rotation/perspective** (unrealistic for fixed CCTV)
- **Result**: 714 augmented images created

### 5. Training & Evaluation (`08_training_evaluation.ipynb`)
- YOLOv8s training with transfer learning from COCO
- AdamW optimizer with cosine learning rate decay
- Early stopping with patience=30
- Model export to ONNX and TorchScript

---

## Quick Start

### Prerequisites

```bash
pip install ultralytics torch torchvision opencv-python albumentations pandas matplotlib
```

### Run Inference

```python
from ultralytics import YOLO

# Load trained model
model = YOLO('runs/retail_theft_yolov8s/weights/best.pt')

# Run inference on image
results = model.predict(
    source='path/to/image.jpg',
    conf=0.25,  # Confidence threshold
    device=0    # GPU (use 'cpu' if no GPU)
)

# Display results
results[0].show()

# Check for theft detection
for box in results[0].boxes:
    if int(box.cls[0]) == 5:  # theft class
        print(f"THEFT DETECTED! Confidence: {float(box.conf[0]):.2f}")
```

### Run on Video Stream

```python
from ultralytics import YOLO

model = YOLO('runs/retail_theft_yolov8s/weights/best.pt')

# RTSP stream
results = model.predict(
    source='rtsp://camera_url',
    stream=True,
    conf=0.25
)

for r in results:
    # Process each frame
    pass
```

---

## Training Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | YOLOv8s | Good balance of speed/accuracy |
| Image Size | 640x640 | Standard YOLO size |
| Batch Size | 2 | Limited by 4GB VRAM |
| Epochs | 100 | Full convergence |
| Optimizer | AdamW | Better regularization |
| Learning Rate | 0.01 → 0.0001 | Cosine decay |
| Early Stopping | 30 epochs | Prevent overfitting |

### Augmentation Settings (Surveillance-Specific)

| Augmentation | Value | Rationale |
|--------------|-------|-----------|
| Horizontal Flip | 0.5 | Realistic for retail |
| HSV Adjustments | Moderate | Lighting variations |
| Mosaic | 1.0 | Effective for detection |
| **Rotation** | **0.0** | Fixed cameras don't rotate |
| **Perspective** | **0.0** | Fixed viewpoint |
| **Vertical Flip** | **0.0** | Unrealistic |

---

## Challenges Overcome

1. **Class Imbalance**: Original dataset had 63% `normal` vs 5% `theft`
   - **Solution**: Targeted augmentation (3x for theft class)

2. **Limited VRAM**: GTX 1650 only has 4GB
   - **Solution**: Batch size=2, disabled caching

3. **Windows DataLoader Crashes**: Multiprocessing issues
   - **Solution**: Set workers=0

4. **Floating-Point Precision**: Bbox coordinates slightly out of [0,1]
   - **Solution**: Fixed 1,257 label files with boundary clamping

5. **AMP Issues on GTX 1650**: NaN losses with mixed precision
   - **Solution**: Disabled AMP training

---

## Future Improvements

1. **Higher Theft Recall**: Lower confidence threshold or use focal loss
2. **More Data**: Collect additional theft samples
3. **Larger Model**: YOLOv8m/l with more VRAM
4. **Video Tracking**: Add ByteTrack for temporal consistency
5. **Edge Deployment**: Optimize with TensorRT/OpenVINO

---

## Hardware Requirements

### Minimum
- NVIDIA GPU with 4GB+ VRAM
- CUDA 11.8+
- 16GB RAM

### Recommended
- NVIDIA RTX 3080/4080 (16GB+ VRAM)
- CUDA 12.x
- 32GB RAM

---

## References

- [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- [Albumentations](https://albumentations.ai/)
- [YOLO Format Specification](https://docs.ultralytics.com/datasets/detect/)

---

## Author

**Shahd Gamil**

