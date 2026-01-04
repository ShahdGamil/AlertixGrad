# Shoplifting Detection Dataset - Merging & Preprocessing Pipeline

> **Comprehensive data preparation pipeline for combining and preprocessing 3 YOLOv8 datasets for shoplifting detection**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.12+-green.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Dataset Information](#dataset-information)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Pipeline Features](#pipeline-features)
- [Output Files](#output-files)
- [Training with YOLOv8](#training-with-yolov8)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

This project provides a complete pipeline for merging and preprocessing three shoplifting detection datasets into a single, unified dataset ready for YOLOv8 training. The pipeline handles:

- **Class mapping** from 6 classes to 2 unified classes
- **Data validation** and quality checks
- **Automatic splitting** into train/validation/test sets
- **Comprehensive preprocessing** with normalization statistics
- **Augmentation configuration** for optimal training
- **Detailed documentation** and visualization

---

## 📊 Dataset Information

### Source Datasets

| Dataset | Name | Images | Classes | License |
|---------|------|--------|---------|---------|
| **B1** | cc-tv-footage-annotation | 2,998 | 6 → 2 | CC BY 4.0 |
| **B2** | shoplifting-detection | 7,111 | 2 | CC BY 4.0 |
| **B3** | test-make | 1,194 | 2 | CC BY 4.0 |
| **TOTAL** | **Merged Dataset** | **~11,303** | **2** | CC BY 4.0 |

### Class Mapping (B1 Dataset)

The B1 dataset originally has 6 classes which are mapped to 2 unified classes:

```
Original Classes          →  Unified Classes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Customer-Bagpack          →  normal (0)
Product                   →  normal (0)
Shopping-Cart             →  normal (0)
normal                    →  normal (0)
Product-Picked            →  theft (1)
theft                     →  theft (1)
```

### Final Dataset Statistics

After merging and preprocessing:

- **Total Images**: ~11,303
- **Classes**: 2 (normal, theft)
- **Train/Val/Test Split**: 70% / 15% / 15%
- **Format**: YOLOv8 (YOLO format annotations)
- **Image Formats**: JPG, PNG

---

## 📁 Project Structure

```
data_mix/
├── README.md                              # This file
├── requirements.txt                       # Python dependencies
├── data_merging_preprocessing.ipynb       # Main preprocessing notebook
│
├── Source Datasets/
│   ├── cc-tv-footage-annotation-b8-lcysc b1.data1.yolov8/
│   │   ├── train/
│   │   ├── valid/
│   │   ├── test/
│   │   └── data.yaml
│   │
│   ├── shoplifting-detection b2.v1-data3.yolov8/
│   │   ├── train/
│   │   ├── valid/
│   │   ├── test/
│   │   └── data.yaml
│   │
│   └── test-make b3.v1-data2.yolov8/
│       ├── train/
│       ├── test/
│       └── data.yaml
│
└── merged_shoplifting_dataset/            # Generated output
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── valid/
    │   ├── images/
    │   └── labels/
    ├── test/
    │   ├── images/
    │   └── labels/
    ├── data.yaml                          # YOLOv8 config
    ├── metadata.json                      # Dataset metadata
    ├── dataset_stats.json                 # Normalization stats
    ├── augmentation_config.yaml           # Training augmentation
    ├── MERGE_REPORT.md                    # Detailed report
    └── *.png                              # Visualizations
```

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Jupyter Lab/Notebook (optional, for running the notebook)

### Step 1: Clone or Download

Download this project to your local machine.

### Step 2: Install Dependencies

```bash
cd c:\Users\NIlEUN\Downloads\data_mix
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python -c "import cv2, numpy, pandas; print('All dependencies installed successfully!')"
```

---

## 💻 Usage

### Option 1: Run Jupyter Notebook (Recommended)

1. **Start Jupyter Lab:**
   ```bash
   jupyter lab
   ```

2. **Open the notebook:**
   - Navigate to `data_merging_preprocessing.ipynb`

3. **Run all cells:**
   - Click: **Run** → **Run All Cells**
   - Or press: **Shift + Enter** for each cell

4. **Wait for completion:**
   - The notebook will process all datasets (~10-15 minutes)
   - Progress bars will show the status

### Option 2: Run as Python Script

Convert the notebook to a script and run:

```bash
jupyter nbconvert --to script data_merging_preprocessing.ipynb
python data_merging_preprocessing.py
```

---

## ✨ Pipeline Features

### 1. **Dataset Analysis**
- Analyzes all 3 source datasets
- Generates statistics on images and annotations
- Visualizes class distributions

### 2. **Class Mapping**
- Automatically maps B1's 6 classes to 2 unified classes
- Validates all class IDs
- Ensures consistency across datasets

### 3. **Data Merging**
- Combines all datasets with proper prefixing
- Prevents naming conflicts
- Validates file integrity

### 4. **Data Validation**
- Checks for missing labels
- Validates bounding box coordinates (0-1 range)
- Identifies corrupted images
- Reports data quality issues

### 5. **Split Reorganization**
- Creates balanced 70/15/15 train/val/test splits
- Randomly shuffles data (with seed for reproducibility)
- Ensures proper distribution

### 6. **Preprocessing**
- Calculates RGB mean and std for normalization
- Generates image statistics
- Prepares data for training

### 7. **Augmentation Configuration**
- Pre-configured augmentation settings for YOLOv8
- Optimized for shoplifting detection
- Includes: rotation, scaling, HSV adjustments, mosaic, mixup

### 8. **Visualization & Reporting**
- Class distribution charts
- Sample annotated images
- Comprehensive markdown report
- Metadata JSON export

---

## 📤 Output Files

After running the pipeline, the following files are generated in `merged_shoplifting_dataset/`:

### Configuration Files

| File | Description |
|------|-------------|
| `data.yaml` | YOLOv8 dataset configuration (required for training) |
| `augmentation_config.yaml` | Training augmentation parameters |
| `dataset_stats.json` | Normalization statistics (mean, std) |
| `metadata.json` | Complete dataset metadata |

### Documentation

| File | Description |
|------|-------------|
| `MERGE_REPORT.md` | Detailed merge and preprocessing report |
| `class_distribution_before_merge.png` | Original class distributions |
| `class_distribution_after_merge.png` | Final unified class distribution |
| `sample_annotations_train.png` | Sample training images with annotations |
| `sample_annotations_valid.png` | Sample validation images |
| `sample_annotations_test.png` | Sample test images |

### Dataset Splits

```
train/      # 70% of data (~7,912 images)
valid/      # 15% of data (~1,695 images)
test/       # 15% of data (~1,696 images)
```

---

## 🎓 Training with YOLOv8

Once the dataset is prepared, you can train a YOLOv8 model:

### Basic Training

```python
from ultralytics import YOLO

# Load a pretrained model
model = YOLO('yolov8n.pt')  # nano
# or: yolov8s.pt (small), yolov8m.pt (medium), yolov8l.pt (large), yolov8x.pt (xlarge)

# Train the model
results = model.train(
    data='c:/Users/NIlEUN/Downloads/data_mix/merged_shoplifting_dataset/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='shoplifting_detection',
    patience=50,
    save=True,
    device=0  # GPU device, or 'cpu'
)
```

### Advanced Training

```python
results = model.train(
    data='c:/Users/NIlEUN/Downloads/data_mix/merged_shoplifting_dataset/data.yaml',
    epochs=200,
    imgsz=640,
    batch=16,
    name='shoplifting_detection_v2',

    # Augmentation (already configured in data.yaml)
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    degrees=10.0,
    translate=0.1,
    scale=0.5,
    fliplr=0.5,
    mosaic=1.0,
    mixup=0.1,

    # Training parameters
    optimizer='AdamW',
    lr0=0.01,
    lrf=0.01,
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=3.0,

    # Regularization
    dropout=0.0,
    label_smoothing=0.1,

    # Validation
    patience=50,
    val=True,

    # Saving
    save=True,
    save_period=10,

    # Hardware
    device=0,
    workers=8,

    # Misc
    seed=42,
    deterministic=True,
    verbose=True
)
```

### Evaluation

```python
# Validate the model
metrics = model.val()

print(f"mAP@50: {metrics.box.map50}")
print(f"mAP@50-95: {metrics.box.map}")
```

### Inference

```python
# Predict on new images
results = model.predict(
    source='path/to/test/images',
    save=True,
    conf=0.25,
    iou=0.45
)

# Process results
for result in results:
    boxes = result.boxes
    for box in boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = model.names[class_id]
        print(f"Detected: {class_name} ({confidence:.2f})")
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **ModuleNotFoundError: No module named 'cv2'**

**Solution:**
```bash
pip install --upgrade opencv-python
```

Then restart your Jupyter kernel.

#### 2. **NumPy compatibility error**

**Error:** `A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x`

**Solution:**
```bash
pip install --upgrade opencv-python numpy>=2.2.0
```

#### 3. **Out of Memory (OOM) during processing**

**Solution:**
- Reduce batch size in image processing
- Process datasets one at a time
- Use a machine with more RAM

#### 4. **Permission denied errors**

**Solution:**
- Run terminal/command prompt as Administrator
- Check folder permissions
- Ensure antivirus isn't blocking file access

#### 5. **Missing validation split for B3 dataset**

**Note:** This is expected and handled automatically by the pipeline. B3's training data will be redistributed across train/val/test splits during reorganization.

---

## 📈 Expected Results

After successful execution:

- ✅ **~11,303 images** merged and organized
- ✅ **2 classes** (normal, theft) with unified labels
- ✅ **Proper splits**: 70% train, 15% val, 15% test
- ✅ **Validated annotations** with quality checks
- ✅ **Normalization statistics** calculated
- ✅ **YOLOv8-ready** dataset configuration
- ✅ **Comprehensive documentation** and visualizations

---

## 🎨 Customization

### Modify Split Ratios

Edit the notebook cell in **Section 6**:

```python
split_stats = reorganize_splits(
    OUTPUT_DIR,
    train_ratio=0.70,  # Change to desired ratio
    val_ratio=0.15,    # Change to desired ratio
    test_ratio=0.15,   # Change to desired ratio
    random_seed=42     # For reproducibility
)
```

### Adjust Augmentation

Edit `augmentation_config.yaml` or modify the notebook in **Section 9**:

```python
augmentation_config = {
    'hsv_h': 0.015,      # HSV-Hue augmentation
    'hsv_s': 0.7,        # HSV-Saturation augmentation
    'hsv_v': 0.4,        # HSV-Value augmentation
    'degrees': 10.0,     # Rotation (+/- deg)
    'translate': 0.1,    # Translation (+/- fraction)
    'scale': 0.5,        # Scaling (+/- gain)
    'fliplr': 0.5,       # Flip left-right probability
    'mosaic': 1.0,       # Mosaic augmentation
    'mixup': 0.1,        # Mixup augmentation
}
```

### Change Class Mapping

Edit the notebook in **Section 4**:

```python
CLASS_MAPPING_B1 = {
    'Customer-Bagpack': 'normal',
    'Product': 'normal',
    'Product-Picked': 'theft',     # Change mapping here
    'Shopping-Cart': 'normal',
    'normal': 'normal',
    'theft': 'theft'
}
```

---

## 📝 Dataset Statistics

### Class Distribution (After Merge)

The final dataset will have approximately:

- **Normal**: ~60-70% of annotations
- **Theft**: ~30-40% of annotations

> **Note:** Exact percentages depend on the source datasets. Check `MERGE_REPORT.md` for precise statistics.

### Image Characteristics

- **Format**: JPG, PNG
- **Typical Size**: 640x480 to 1920x1080
- **Color Space**: RGB
- **Annotations**: YOLO format (normalized coordinates)

---

## 🤝 Contributing

Contributions are welcome! If you find bugs or have suggestions:

1. Open an issue describing the problem
2. Submit a pull request with improvements
3. Share your training results and insights

---

## 📜 License

This dataset merging pipeline is provided for educational and research purposes.

- **Source Datasets**: CC BY 4.0 (Roboflow)
- **Pipeline Code**: MIT License
- **Merged Dataset**: Inherits CC BY 4.0 from source datasets

---

## 🙏 Acknowledgments

- **Roboflow** for providing the source datasets
- **Ultralytics** for the YOLOv8 framework
- **OpenCV** and **scikit-learn** communities

---

## 📞 Support

For questions or issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the `MERGE_REPORT.md` after running the pipeline
3. Inspect the generated `metadata.json` for detailed statistics

---

## 🚦 Quick Start Checklist

- [ ] Install Python 3.11+
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify OpenCV: `python -c "import cv2; print(cv2.__version__)"`
- [ ] Open Jupyter: `jupyter lab`
- [ ] Run notebook: `data_merging_preprocessing.ipynb`
- [ ] Check output: `merged_shoplifting_dataset/`
- [ ] Review report: `MERGE_REPORT.md`
- [ ] Start training with YOLOv8!

---

## 📊 Performance Metrics

After training, you should track:

- **mAP@50**: Mean Average Precision at IoU=0.5
- **mAP@50-95**: Mean Average Precision at IoU=0.5:0.95
- **Precision**: True Positives / (True Positives + False Positives)
- **Recall**: True Positives / (True Positives + False Negatives)
- **F1-Score**: Harmonic mean of Precision and Recall

Expected baseline results (after 100 epochs with YOLOv8n):
- mAP@50: 0.70 - 0.85
- mAP@50-95: 0.45 - 0.65

> **Note:** Results vary based on model size, training duration, and augmentation settings.

---

**Happy Training! 🚀**

*Last Updated: 2026-01-03*
