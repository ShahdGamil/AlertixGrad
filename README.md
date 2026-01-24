# YOLO Ensemble Theft Detection Pipeline

## Production-Ready Computer Vision Pipeline for Retail Surveillance

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-green)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive, production-grade pipeline for training YOLO ensemble models optimized for high-recall theft detection in retail environments.

---

## 🎯 Features

### ✅ Dataset Processing
- **Strict YOLO Format Validation** - Validates annotations, bounding boxes, and class IDs
- **Automated Cleaning** - Removes corrupt images, invalid labels, and duplicates
- **Smart Balancing** - Ensemble-aware class balancing with targeted augmentation
- **YOLOv8 Preprocessing** - Letterbox padding, aspect ratio preservation, normalization
- **Stratified Splitting** - Leak-free train/val/test splits with class stratification

### ✅ Retail-Safe Augmentation
- Horizontal flip, brightness/contrast, motion blur, Gaussian noise
- Mosaic augmentation, color jitter, random scaling
- **No unrealistic transformations** (rotation, vertical flip, heavy warping)

### ✅ Ensemble Training
- Multi-model support: YOLOv8n, YOLOv8s, YOLOv8m
- Automated training script generation
- Transfer learning from pretrained weights
- Class-weighted loss for imbalance handling

### ✅ Visualization & Analysis
- Class distribution charts
- Bounding box statistics
- Image resolution analysis
- Labeled sample grids
- Comprehensive Jupyter notebook

### ✅ Production Ready
- Modular architecture with clean separation of concerns
- Extensive logging and error handling
- JSON and text report generation
- Configurable via YAML
- Type hints and docstrings

---

## 📊 Dataset Overview

| Class | Count | Purpose |
|-------|-------|---------|
| Customer-Bagpack | 780 | Customer with backpack |
| Normal | 6,443 | Normal shopping behavior |
| Product | 1,061 | Product on shelf |
| Product-Picked | 1,051 | Product being picked |
| Shopping-Cart | 212 | Shopping cart detection |
| **Theft** | **600** | **Priority class - theft behavior** |

**Total:** 10,147 instances across 6 classes

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd yolo_ensemble_pipeline

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Prepare Your Dataset

Organize your dataset in YOLO format:

```
your_dataset/
├── images/
│   ├── img_001.jpg
│   ├── img_002.jpg
│   └── ...
└── labels/
    ├── img_001.txt
    ├── img_002.txt
    └── ...
```

**Label Format:** `class_id x_center y_center width height` (normalized 0-1)

### 3. Configure Pipeline

Edit [config/config.yaml](config/config.yaml) to customize:
- Class names and counts
- Balancing strategy
- Augmentation parameters
- Training hyperparameters
- Paths and output directories

### 4. Run Pipeline

```bash
python pipeline.py --images path/to/images --labels path/to/labels
```

The pipeline will execute all stages:
1. ✅ Validation
2. ✅ Cleaning
3. ✅ Balancing
4. ✅ Preprocessing
5. ✅ Splitting
6. ✅ Visualization
7. ✅ Training Preparation

### 5. Train Ensemble Models

```bash
cd outputs/models
python train_ensemble.py
```

Or use the provided scripts:
- **Windows:** `train_ensemble.bat`
- **Linux/Mac:** `train_ensemble.sh`

### 6. Analyze Results

Open and run the Jupyter notebook:

```bash
jupyter notebook analysis_notebook.ipynb
```

---

## 📁 Project Structure

```
yolo_ensemble_pipeline/
├── config/
│   └── config.yaml              # Main configuration file
├── src/
│   ├── validation/
│   │   └── dataset_validator.py # YOLO format validation
│   ├── cleaning/
│   │   └── dataset_cleaner.py   # Dataset cleaning
│   ├── balancing/
│   │   └── dataset_balancer.py  # Class balancing
│   ├── preprocessing/
│   │   └── preprocessor.py      # Image preprocessing
│   ├── splitting/
│   │   └── dataset_splitter.py  # Train/val/test split
│   ├── visualization/
│   │   └── visualizer.py        # Visualization & analysis
│   ├── training/
│   │   └── ensemble_trainer.py  # Training preparation
│   └── utils/
│       ├── logger.py            # Logging system
│       └── config_loader.py     # Config management
├── pipeline.py                  # Main orchestrator
├── analysis_notebook.ipynb      # Analysis notebook
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

---

## ⚙️ Configuration

### Key Configuration Sections

#### Dataset Configuration
```yaml
dataset:
  classes:
    - "Customer-Bagpack"
    - "Normal"
    - "Product"
    - "Product-Picked"
    - "Shopping-Cart"
    - "Theft"
  priority_class: "Theft"
```

#### Balancing Strategy
```yaml
balancing:
  strategy: "ensemble_aware"
  apply_to_classes:
    Theft: 3.0           # Oversample 3x
    Shopping-Cart: 2.5   # Oversample 2.5x
    Normal: 0.5          # Undersample to 50%
```

#### Training Hyperparameters
```yaml
yolo_training:
  hyperparameters:
    epochs: 100
    batch_size: 16
    imgsz: 640
    optimizer: "AdamW"
    lr0: 0.001
    patience: 20
```

#### Ensemble Configuration
```yaml
ensemble:
  strategy: "weighted_box_fusion"
  class_weights:
    Theft: 1.5          # Boost theft detection
  theft_conf_threshold: 0.15  # Lower threshold for high recall
```

See [config/config.yaml](config/config.yaml) for full configuration options.

---

## 📊 Pipeline Workflow

### Stage 1: Validation
- ✓ Check YOLO annotation format
- ✓ Validate bounding box normalization
- ✓ Detect missing/corrupt files
- ✓ Verify class ID ranges
- ✓ Auto-fix minor issues

### Stage 2: Cleaning
- ✓ Remove corrupt images
- ✓ Remove invalid bounding boxes
- ✓ Detect and remove duplicates (perceptual hashing)
- ✓ Normalize file naming
- ✓ Ensure strict image-label pairing

### Stage 3: Balancing
- ✓ Analyze class distribution
- ✓ Apply ensemble-aware sampling
- ✓ Oversample minority classes (Theft, Shopping-Cart)
- ✓ Undersample majority class (Normal)
- ✓ Augment underrepresented classes

### Stage 4: Preprocessing
- ✓ Resize to 640×640 with letterbox padding
- ✓ Maintain aspect ratio
- ✓ Auto-orient images
- ✓ Normalize pixel values
- ✓ Convert to training format

### Stage 5: Splitting
- ✓ Stratified split: 70% train / 20% val / 10% test
- ✓ Class-balanced splits
- ✓ No data leakage
- ✓ Reproducible (fixed seed)

### Stage 6: Visualization
- ✓ Class distribution charts
- ✓ Bounding box statistics
- ✓ Image resolution analysis
- ✓ Sample grids with annotations
- ✓ Split statistics

### Stage 7: Training Preparation
- ✓ Generate `data.yaml` for YOLOv8
- ✓ Create model-specific configs
- ✓ Generate training scripts
- ✓ Prepare ensemble configuration

---

## 🎓 Training Recommendations

### For High-Recall Theft Detection:

1. **Use Ensemble Approach**
   - YOLOv8n: Fast baseline (30+ FPS)
   - YOLOv8s: Balanced performance (recommended)
   - YOLOv8m: Maximum accuracy (if GPU available)

2. **Optimize for Recall**
   - Lower confidence threshold for Theft class (0.15)
   - Use class weights: Theft=1.5, Normal=0.8
   - Apply focal loss for hard examples
   - Longer training with patience=20

3. **Handle Class Imbalance**
   - Oversample Theft 3x
   - Undersample Normal to 50%
   - Use class-weighted loss
   - Monitor per-class metrics

4. **Augmentation Strategy**
   - Heavy augmentation on minority classes
   - Mosaic augmentation for context
   - Conservative brightness/contrast
   - No unrealistic transforms

5. **Ensemble Fusion**
   - Weighted Box Fusion (WBF) with IoU=0.5
   - Model weights: n=0.3, s=0.4, m=0.3
   - Confidence aggregation: weighted_avg
   - Class-specific threshold tuning

---

## 📈 Expected Performance

### Single Model Baseline (YOLOv8s):
- **mAP50:** ~0.75-0.85
- **Theft Recall:** ~0.80-0.90
- **Inference:** ~40 FPS (GPU)

### Ensemble (n+s+m):
- **mAP50:** ~0.80-0.90 (+5-10%)
- **Theft Recall:** ~0.85-0.95 (+5-7%)
- **Inference:** ~15-20 FPS (GPU, sequential)

### Trade-offs:
- ⚡ Speed: YOLOv8n (fastest)
- ⚖️ Balance: YOLOv8s (recommended)
- 🎯 Accuracy: Ensemble (best)

---

## 🔧 Advanced Usage

### Custom Configuration

```python
from utils.config_loader import ConfigLoader

config = ConfigLoader('config/config.yaml')
config.get('dataset.priority_class')  # Access nested keys
```

### Programmatic Pipeline

```python
from pipeline import YOLOEnsemblePipeline

pipeline = YOLOEnsemblePipeline('config/config.yaml')
pipeline.run_full_pipeline('path/to/images', 'path/to/labels')
```

### Individual Modules

```python
from validation.dataset_validator import YOLODatasetValidator
from utils.logger import get_logger

logger = get_logger()
validator = YOLODatasetValidator(logger, config)
results = validator.validate_dataset(images_dir, labels_dir)
```

---

## 📝 Output Files

After running the pipeline, you'll find:

```
data/
├── cleaned/              # Cleaned dataset
├── processed/
│   ├── balanced/         # Balanced dataset
│   └── preprocessed/     # Preprocessed images
└── train_ready/          # Train/val/test splits
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── val/
    └── test/

outputs/
├── logs/                 # Pipeline logs
├── reports/              # JSON & text reports
├── visualizations/       # Analysis plots
└── models/               # Training configs
    ├── data.yaml
    ├── yolov8n_config.yaml
    ├── yolov8s_config.yaml
    ├── train_ensemble.py
    └── train_ensemble.bat
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** `FileNotFoundError: Images directory not found`
- **Solution:** Ensure correct paths to images/ and labels/ directories

**Issue:** Validation fails with bbox errors
- **Solution:** Enable `auto_fix: true` in config.yaml

**Issue:** Out of memory during training
- **Solution:** Reduce `batch_size` in config.yaml (try 8 or 4)

**Issue:** Low recall on Theft class
- **Solution:**
  - Increase `apply_to_classes.Theft` to 4.0 or 5.0
  - Lower `theft_conf_threshold` to 0.10
  - Increase training epochs

**Issue:** Slow training
- **Solution:**
  - Disable heavy models (yolov8m)
  - Use `cache: "ram"` for faster data loading
  - Reduce image size to 416 (trade-off with accuracy)

---

## 🔬 Evaluation Metrics

### Primary Metrics (Theft Detection):
- **Recall:** Must be ≥0.90 (capture all theft instances)
- **Precision:** Target ≥0.75 (control false alarms)
- **F1-Score:** Harmonic mean of precision/recall

### Overall Metrics:
- **mAP50:** Mean average precision @ IoU=0.50
- **mAP50-95:** mAP across IoU thresholds
- **Inference Time:** FPS on target hardware

### Per-Class Analysis:
- Monitor confusion matrix
- Analyze false positives/negatives
- Class-specific precision/recall curves

---

## 🚀 Deployment Considerations

### Production Checklist:
- [ ] Train ensemble on full dataset
- [ ] Validate on held-out test set
- [ ] Benchmark inference speed on target hardware
- [ ] Implement confidence threshold tuning
- [ ] Set up model versioning
- [ ] Create inference API/service
- [ ] Implement alert system for Theft detections
- [ ] Add logging and monitoring
- [ ] Prepare fallback mechanism
- [ ] Document model limitations

### Inference Optimization:
- Use TensorRT/ONNX for faster inference
- Batch processing for multiple streams
- Model quantization (FP16/INT8)
- Edge deployment considerations

---

## 📚 Resources

### Documentation:
- [YOLOv8 Official Docs](https://docs.ultralytics.com/)
- [Albumentations](https://albumentations.ai/)
- [Ensemble Methods](https://github.com/ZFTurbo/Weighted-Boxes-Fusion)

### Training Guides:
- Transfer learning best practices
- Hyperparameter tuning strategies
- Class imbalance handling techniques

### Related Papers:
- YOLOv8 Architecture
- Focal Loss for Dense Object Detection
- Weighted Boxes Fusion

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional augmentation strategies
- Advanced ensemble methods (NMS variants)
- Multi-GPU training support
- TensorRT optimization
- Real-time inference examples

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Senior Computer Vision & MLOps Engineer**
Specializing in YOLO-based ensemble detection systems

---

## 🙏 Acknowledgments

- Ultralytics for YOLOv8
- Albumentations team
- OpenCV community
- PyTorch team

---

## 📞 Support

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Review configuration documentation
3. Open an issue on GitHub
4. Contact the maintainer

---

**Built with ❤️ for Production ML Systems**

*Last Updated: 2026-01-19*
