# YOLOv8 Ensemble for Retail Theft Detection

A deep learning project that uses an ensemble of YOLOv8 models with Weighted Boxes Fusion (WBF) for detecting shoplifting and theft in retail environments.

## Overview

This project implements an ensemble approach using three YOLOv8 variants (nano, small, medium) to detect various objects and behaviors in retail surveillance footage. The models are combined using both NMS (Non-Maximum Suppression) and WBF (Weighted Boxes Fusion) techniques to improve detection accuracy.

## Dataset

| Split | Images |
|-------|--------|
| Train | 2,095 |
| Valid | 600 |
| Test | 303 |

### Classes (6 total)

| ID | Class Name | Description | Priority |
|----|------------|-------------|----------|
| 0 | Customer-Bagpack | Customer carrying a backpack | Medium |
| 1 | Product | Store product on shelf | Low |
| 2 | Product-Picked | Product being picked up | Low |
| 3 | Shopping-Cart | Shopping cart | High |
| 4 | Normal | Normal customer behavior | Low |
| 5 | Theft | Shoplifting/theft behavior | **Highest** |

## Models

The ensemble consists of three YOLOv8 models:

| Model | Variant | Parameters | GFLOPs |
|-------|---------|------------|--------|
| YOLOv8n | Nano | ~3.2M | 8.7 |
| YOLOv8s | Small | ~11.2M | 28.6 |
| YOLOv8m | Medium | ~25.9M | 78.9 |

## Training Configuration

```python
EPOCHS = 50
IMG_SIZE = 640
BATCH_SIZE = 16
CONF_THRESHOLD = 0.25
IOU_THRESHOLD = 0.5
OPTIMIZER = "AdamW"
LR0 = 0.001
```

## Results

### Ensemble Comparison

| Metric | NMS Ensemble | WBF Ensemble |
|--------|--------------|--------------|
| Precision | 0.8850 | 0.8556 |
| Recall | 0.9322 | 0.9487 |
| F1-Score | **0.9080** | 0.8997 |
| True Positives | 908 | 924 |
| False Positives | 118 | 156 |
| False Negatives | 66 | 50 |

**Winner:** NMS Ensemble (F1 better by 0.83%)

### Per-Class Performance (NMS Ensemble)

| Class | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| Customer-Bagpack | 0.7703 | 0.9048 | 0.8321 |
| Product | 0.6900 | 0.7753 | 0.7302 |
| Product-Picked | 0.8571 | 0.8936 | 0.8750 |
| Shopping-Cart | 0.8333 | 0.9091 | 0.8696 |
| Normal | 0.9359 | 0.9691 | **0.9522** |
| Theft | 0.8475 | 0.8621 | 0.8547 |

## Installation

```bash
pip install ultralytics ensemble-boxes supervision opencv-python
```

## Quick Start

```bash
# 1. Navigate to pipeline directory
cd yolo_ensemble_pipeline

# 2. Run the data preparation pipeline
python src/pipeline.py --source "path/to/your/dataset"

# 3. Train ensemble models
python outputs/train_ensemble.py
```

## Usage

### Training

```python
from ultralytics import YOLO

# Train individual models
for model_name, weights in [("yolov8n", "yolov8n.pt"),
                             ("yolov8s", "yolov8s.pt"),
                             ("yolov8m", "yolov8m.pt")]:
    model = YOLO(weights)
    model.train(
        data="data.yaml",
        epochs=50,
        imgsz=640,
        batch=16,
        device=0,
        project="yolo_ensemble",
        name=model_name
    )
```

### Inference with Ensemble

```python
from ultralytics import YOLO
from ensemble_boxes import weighted_boxes_fusion

# Load trained models
models = {
    "yolov8n": YOLO("path/to/yolov8n/weights/best.pt"),
    "yolov8s": YOLO("path/to/yolov8s/weights/best.pt"),
    "yolov8m": YOLO("path/to/yolov8m/weights/best.pt")
}

# Run predictions
results = {}
for name, model in models.items():
    results[name] = model.predict(source="test/images", conf=0.25)

# Apply WBF ensemble
# weights = [1.0, 0.3, 1.0]  # Adjust based on model performance
```

## Pipeline Stages

1. **Validation** - Checks dataset integrity (YOLO format, bbox validation)
2. **Cleaning** - Removes corrupt/invalid data
3. **Splitting** - Creates stratified train/val/test splits (70/20/10)
4. **Balancing** - Handles class imbalance with targeted oversampling
5. **Preprocessing** - Prepares data for YOLOv8
6. **Visualization** - Generates analysis reports
7. **Configuration** - Creates training configs

## Project Structure

```
yolo_ensemble_pipeline/
├── configs/                    # Configuration files
├── src/                        # Source code
│   ├── pipeline.py            # Main pipeline script
│   └── config.py              # Configuration settings
├── outputs/
│   ├── 01_cleaned/            # Cleaned dataset
│   ├── 02_split/              # Train/Val/Test splits
│   ├── 03_balanced/           # Balanced training data
│   ├── 04_final/              # Final training-ready dataset
│   │   ├── train/images/
│   │   ├── train/labels/
│   │   ├── val/images/
│   │   ├── val/labels/
│   │   ├── test/images/
│   │   ├── test/labels/
│   │   └── data.yaml
│   ├── train_ensemble.py      # Training script
│   └── ensemble_inference.py  # Inference script
├── logs/                       # Processing/training logs
├── visualizations/             # Analysis reports
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Ensemble Strategy

- **Models**: YOLOv8n + YOLOv8s + YOLOv8m
- **Fusion Methods**:
  - NMS (Non-Maximum Suppression) - Better F1 score
  - WBF (Weighted Box Fusion) - Better recall
- **Model Weights**: `[1.0, 0.3, 1.0]` (downweight underperforming YOLOv8s)
- **Threshold**: Lower confidence for theft (0.20) vs normal (0.45)
- **Optimization**: High recall on theft class

## Key Features

- **Multi-model Ensemble:** Combines predictions from YOLOv8n, YOLOv8s, and YOLOv8m
- **WBF Integration:** Uses Weighted Boxes Fusion for better box localization
- **Model Weighting:** Supports custom weights for each model based on performance
- **Class Balancing:** Targeted oversampling for minority classes
- **Colab Ready:** Designed to run on Google Colab with GPU support (Tesla T4)

## Recommendations for Improvement

1. **Retrain underperforming models** - YOLOv8s showed lower performance and may need retraining
2. **Address class imbalance** - Consider oversampling minority classes (Theft, Shopping-Cart)
3. **Increase training epochs** - Try 100+ epochs with early stopping
4. **Tune WBF parameters** - Adjust IoU threshold and model weights
5. **Data augmentation** - Add more augmentation for rare classes

## Hardware Requirements

- **Training:** GPU with 4GB+ VRAM (tested on Tesla T4 - 15GB)
- **Inference:** GPU recommended, CPU supported
- **Platform:** Google Colab / Local with CUDA support

## Configuration

Edit `src/config.py` to customize:
- Class weights
- Augmentation parameters
- Training hyperparameters
- Split ratios
- Ensemble model weights

## Requirements

- Python 3.8+
- ultralytics
- ensemble-boxes
- supervision
- opencv-python
- torch (CUDA-capable for faster training)

## License

CC BY 4.0 (inherited from dataset)

## Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Weighted Boxes Fusion](https://github.com/ZFTurbo/Weighted-Boxes-Fusion)
- Dataset prepared with [Roboflow](https://roboflow.com/)
