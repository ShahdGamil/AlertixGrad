# Retail Theft Detection with YOLOv8s

A comprehensive computer vision pipeline for retail surveillance theft detection using **YOLOv8 Small (YOLOv8s)**.

## Project Overview

This project provides a complete end-to-end pipeline for:
- **Dataset validation and cleaning** for YOLO format annotations
- **Class imbalance handling** through targeted augmentation
- **YOLOv8s model training** optimized for retail surveillance
- **High recall theft detection** as the primary objective

### Target Application
Real-time retail theft detection from CCTV surveillance footage.

### Dataset Classes
| Class ID | Class Name | Description |
|----------|------------|-------------|
| 0 | Customer-Bagpack | Customer carrying a backpack |
| 1 | Product | Store products on shelves |
| 2 | Product-Picked | Products being handled |
| 3 | Shopping-Cart | Shopping carts in frame |
| 4 | normal | Normal shopping behavior |
| 5 | **theft** | Theft/suspicious activity (priority class) |

---

## Directory Structure

```
AletrixGrad/
├── cc-tv-footage-annotation-b8-lcysc-b1-2/   # Original dataset
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── valid/
│   │   ├── images/
│   │   └── labels/
│   ├── test/
│   │   ├── images/
│   │   └── labels/
│   └── data.yaml
├── notebooks/                    # Jupyter notebooks (main pipeline)
│   ├── 01_dataset_validation.ipynb
│   ├── 02_dataset_cleaning.ipynb
│   ├── 03_dataset_analysis.ipynb
│   ├── 04_dataset_balancing.ipynb
│   ├── 05_dataset_splitting.ipynb
│   ├── 06_preprocessing_pipeline.ipynb
│   ├── 07_training_preparation.ipynb
│   └── 08_training_evaluation.ipynb
├── configs/                      # Configuration files
│   ├── data.yaml
│   └── training_config.yaml
├── outputs/                      # Reports and logs
├── visualizations/               # Generated charts and images
├── runs/                         # Training outputs
├── dataset_cleaned/              # Cleaned dataset (generated)
├── dataset_augmented/            # Augmented dataset (generated)
├── train_yolov8s.py              # Training script
└── README.md                     # This file
```

---

## Quick Start

### Prerequisites

1. **Python 3.8+**
2. **NVIDIA GPU with CUDA** (strongly recommended)
3. **PyTorch with CUDA support**

### Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install ultralytics torch torchvision opencv-python pillow numpy pandas matplotlib seaborn albumentations tqdm pyyaml scikit-learn imagehash jupyter

# Verify GPU
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Running the Pipeline

**Option 1: Execute notebooks sequentially**
```bash
cd notebooks
jupyter notebook
# Run notebooks 01 through 08 in order
```

**Option 2: Use the training script directly**
```bash
python train_yolov8s.py
```

**Option 3: Command line training**
```bash
yolo detect train data=configs/data.yaml model=yolov8s.pt epochs=100 batch=16 imgsz=640 device=0
```

---

## Notebook Execution Order

Execute notebooks in the following sequence:

### 1. Dataset Validation (`01_dataset_validation.ipynb`)
**Purpose:** Verify dataset integrity and identify issues

**What it does:**
- Validates YOLO label format (class_id x_center y_center width height)
- Detects missing/corrupt images
- Validates bounding box normalization (values in [0, 1])
- Identifies orphan labels (labels without images)
- Generates validation report with statistics

**Key outputs:**
- `outputs/validation_report.json`
- `visualizations/validation_*.png`

---

### 2. Dataset Cleaning (`02_dataset_cleaning.ipynb`)
**Purpose:** Fix issues and remove problematic samples

**What it does:**
- Removes corrupt/unreadable images
- Fixes invalid bounding box coordinates
- Removes duplicate images (perceptual hashing)
- Creates empty labels for images without annotations
- Removes orphan labels

**Key outputs:**
- `dataset_cleaned/` - Cleaned dataset
- `outputs/cleaning_report.json`
- `logs/cleaning_log.json`

---

### 3. Dataset Analysis (`03_dataset_analysis.ipynb`)
**Purpose:** Comprehensive dataset visualization and insights

**What it does:**
- Class distribution analysis
- Bounding box size/aspect ratio distributions
- Image resolution analysis
- Annotations per image statistics
- Sample image visualization with bboxes

**Key outputs:**
- `visualizations/class_distribution.png`
- `visualizations/bbox_distribution.png`
- `outputs/dataset_analysis_report.json`

---

### 4. Dataset Balancing (`04_dataset_balancing.ipynb`)
**Purpose:** Address class imbalance through augmentation

**What it does:**
- Analyzes class imbalance severity
- Applies targeted augmentation to minority classes:
  - **theft** (3x augmentation)
  - **Shopping-Cart** (2x augmentation)
- Uses realistic surveillance augmentations:
  - Horizontal flip
  - Brightness/contrast adjustment
  - Motion blur
  - Gaussian noise
  - Color jitter

**Key outputs:**
- `dataset_augmented/` - Balanced dataset
- `outputs/augmentation_report.json`
- `visualizations/augmentation_*.png`

---

### 5. Dataset Splitting (`05_dataset_splitting.ipynb`)
**Purpose:** Verify/create stratified train/val/test splits

**What it does:**
- Analyzes current split ratios (target: 70/20/10)
- Checks class distribution consistency across splits
- Detects data leakage (overlapping images)
- Optional: Creates new stratified split

**Key outputs:**
- `outputs/split_statistics_report.json`
- `visualizations/split_distribution.png`

---

### 6. Preprocessing Pipeline (`06_preprocessing_pipeline.ipynb`)
**Purpose:** Prepare images for optimal training

**What it does:**
- Auto-orients images using EXIF metadata
- Resizes to 640x640 with letterboxing
- Preserves aspect ratio with padding
- Transforms bounding box coordinates

**Note:** YOLOv8 handles preprocessing internally, so this step is optional but useful for dataset caching.

**Key outputs:**
- `dataset_processed/` - Preprocessed dataset
- `outputs/preprocessing_report.json`

---

### 7. Training Preparation (`07_training_preparation.ipynb`)
**Purpose:** Configure everything for YOLOv8s training

**What it does:**
- GPU verification and diagnostics
- Calculates optimal batch size based on GPU memory
- Computes class weights for imbalanced data
- Generates optimized `data.yaml`
- Creates training configuration file
- Generates training script

**Key outputs:**
- `configs/data.yaml`
- `configs/training_config.yaml`
- `train_yolov8s.py`
- `outputs/training_recommendations.txt`

---

### 8. Training & Evaluation (`08_training_evaluation.ipynb`)
**Purpose:** Train YOLOv8s and evaluate performance

**What it does:**
- Verifies GPU availability (CRITICAL)
- Trains YOLOv8s with optimized hyperparameters
- Monitors training progress
- Evaluates on validation and test sets
- Generates per-class metrics (focus on theft recall)
- Exports model (ONNX, TorchScript)

**Key outputs:**
- `runs/retail_theft_yolov8s/weights/best.pt`
- `runs/retail_theft_yolov8s/results.csv`
- `visualizations/training_curves.png`
- `outputs/training_final_report.json`

---

## GPU Requirements

### Minimum Requirements
- **GPU:** NVIDIA GPU with 6GB+ VRAM
- **CUDA:** 11.8 or 12.x
- **cuDNN:** 8.x+

### Recommended Setup
- **GPU:** NVIDIA RTX 3080/4080 or better (16GB+ VRAM)
- **Batch size:** 16-32 (adjust based on VRAM)

### Verify GPU Setup
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"CUDA version: {torch.version.cuda}")
```

### Install PyTorch with CUDA
```bash
# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

---

## Training Configuration

### Hyperparameters (Optimized for Retail Surveillance)

| Parameter | Value | Description |
|-----------|-------|-------------|
| Model | YOLOv8s | Small model, good balance |
| Image Size | 640x640 | Standard YOLO size |
| Epochs | 100 | With early stopping |
| Batch Size | 8-32 | Based on GPU memory |
| Optimizer | AdamW | Better generalization |
| Learning Rate | 0.01 | With cosine decay |
| Warmup Epochs | 3 | Gradual learning |
| Early Stopping | 30 epochs | Prevent overfitting |

### Augmentation Settings (Surveillance-Specific)

| Augmentation | Value | Rationale |
|--------------|-------|-----------|
| Mosaic | 1.0 | Effective for detection |
| Horizontal Flip | 0.5 | Realistic for retail |
| HSV Adjustments | Moderate | Lighting variations |
| **Rotation** | **0.0** | Fixed cameras |
| **Shear** | **0.0** | Unrealistic distortion |
| **Perspective** | **0.0** | Fixed viewpoint |
| **Vertical Flip** | **0.0** | Unrealistic |

---

## Maximizing Theft Class Recall

### Strategies Implemented

1. **Targeted Augmentation**
   - 3x augmentation multiplier for theft samples
   - Realistic augmentations (brightness, blur, noise)

2. **Class Weights**
   - Calculated using sqrt-inverse-frequency
   - Higher weight for minority classes

3. **Training Optimizations**
   - Higher classification loss weight
   - Early stopping monitors mAP

### Inference Recommendations

For maximum theft recall:
```python
# Use lower confidence threshold
model.predict(source=images, conf=0.25)  # Instead of 0.5

# For real-time monitoring, prioritize recall
model.predict(source=stream, conf=0.2, iou=0.4)
```

---

## Model Export & Deployment

### Export Trained Model

```python
from ultralytics import YOLO

model = YOLO('runs/retail_theft_yolov8s/weights/best.pt')

# Export to ONNX (recommended for production)
model.export(format='onnx', imgsz=640)

# Export to TensorRT (fastest inference on NVIDIA)
model.export(format='engine', imgsz=640)

# Export for edge devices
model.export(format='tflite', imgsz=640)
```

### Inference Example

```python
from ultralytics import YOLO

# Load trained model
model = YOLO('runs/retail_theft_yolov8s/weights/best.pt')

# Single image
results = model.predict('path/to/image.jpg', conf=0.25)

# Video stream
results = model.predict('rtsp://camera_url', stream=True)

# Process results
for r in results:
    boxes = r.boxes  # Bounding boxes
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        if cls == 5:  # theft class
            print(f"THEFT DETECTED! Confidence: {conf:.2f}")
```

---

## Troubleshooting

### Common Issues

#### 1. "No GPU detected"
```bash
# Check NVIDIA driver
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### 2. "Out of Memory (OOM)"
```python
# Reduce batch size
model.train(batch=4, ...)

# Disable caching
model.train(cache=False, ...)

# Use smaller image size
model.train(imgsz=512, ...)
```

#### 3. "Low Theft Recall"
- Increase augmentation multiplier for theft class
- Lower confidence threshold during inference
- Fine-tune with higher `cls` loss weight
- Add more theft samples if available

#### 4. "Training Too Slow"
```python
# Verify GPU usage
print(f"Device: {torch.cuda.current_device()}")

# Enable caching
model.train(cache=True, ...)

# Enable AMP
model.train(amp=True, ...)
```

---

## Results Interpretation

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| mAP@0.5 | Mean AP at IoU 0.5 | > 0.7 |
| mAP@0.5:0.95 | Mean AP across IoUs | > 0.5 |
| **Theft Recall** | Detection rate for theft | **> 0.8** |
| Precision | Accuracy of detections | > 0.7 |

### Understanding Results

- **High Recall, Low Precision:** Many false positives (adjust conf threshold up)
- **Low Recall, High Precision:** Missing detections (adjust conf threshold down)
- **Low mAP:** Model underfitting (train longer, increase data augmentation)

---

## File Outputs Summary

| File | Location | Description |
|------|----------|-------------|
| `best.pt` | `runs/retail_theft_yolov8s/weights/` | Best trained model |
| `results.csv` | `runs/retail_theft_yolov8s/` | Training metrics per epoch |
| `data.yaml` | `configs/` | Dataset configuration |
| `validation_report.json` | `outputs/` | Dataset validation results |
| `training_final_report.json` | `outputs/` | Final training summary |
| `training_curves.png` | `visualizations/` | Loss and metric plots |

---

## Citation

If you use this pipeline in your research, please cite:

```bibtex
@misc{retail_theft_yolov8,
  title={Retail Theft Detection with YOLOv8s},
  author={AletrixGrad Project},
  year={2024},
  howpublished={GitHub Repository}
}
```

---

## License

This project uses:
- **YOLOv8** by Ultralytics (AGPL-3.0)
- **Dataset** from Roboflow (CC BY 4.0)



*Generated for the AletrixGrad Retail Theft Detection Project*
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
======================================================================
TRAINING AND EVALUATION COMPLETE
======================================================================

FINAL SUMMARY
=============

Model: YOLOv8s (Small)
Dataset: dataset_augmented

VALIDATION METRICS:
  mAP@0.5:      0.8448
  mAP@0.5:0.95: 0.6374
  Precision:    0.8220
  Recall:       0.8084

TEST METRICS:
  mAP@0.5:      0.7874
  mAP@0.5:0.95: 0.5793
  Precision:    0.7398
  Recall:       0.7919

MODEL FILES:
  Best weights: C:\Users\shaho\OneDrive - Nile University\Desktop\AletrixGrad\runs\retail_theft_yolov8s\weights\best.pt
  ONNX export:  C:\Users\shaho\OneDrive - Nile University\Desktop\AletrixGrad\runs\retail_theft_yolov8s\weights\best.onnx

======================================================================

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
