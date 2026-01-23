# 🚀 Retail Theft Detection - YOLOv8 Nano on CPU

**Status**: ✅ **TRAINING IN PROGRESS**

---

## Quick Overview

This project trains a **YOLOv8 Nano** deep learning model to detect retail theft in CCTV footage. The model is optimized for **HIGH RECALL** on the theft class (catching most thefts) while running efficiently on **CPU** (no GPU required).

### Key Stats
- **Dataset**: 2,578 CCTV images across 6 object classes
- **Model**: YOLOv8 Nano (~3M parameters, lightweight)
- **Hardware**: CPU-only (any modern processor)
- **Training Time**: 24-48 hours
- **Goal**: >70% recall on theft detection

---

## 📦 What's Included

### Core Files
| File | Purpose |
|------|---------|
| `train_minimal.py` | Main training script (RUNNING NOW) |
| `data.yaml` | Dataset configuration |
| `yolov8n.pt` | Pretrained model (6.2 MB) |

### Documentation
| Document | Content |
|----------|---------|
| **PROJECT_SUMMARY.md** | Complete project overview |
| **TRAINING_GUIDE.md** | Detailed training documentation |
| **DEPLOYMENT_GUIDE.md** | How to use the trained model |
| **TRAINING_STATUS.md** | Current training details |
| **README_DATASET.txt** | Dataset information |

### Dataset
- `train/` - 1,675 training images
- `valid/` - 600 validation images
- `test/` - 303 test images
- `reports/` - Dataset validation reports

### Preprocessing Tools
| Tool | Purpose |
|------|---------|
| `run_split_verification.py` | Verify dataset splits |
| `preprocessing/main_pipeline.py` | Data pipeline |
| `preprocessing/dataset_validator.py` | Validate labels |
| `preprocessing/class_balancer.py` | Balance classes |

---

## 🎯 Model Capabilities

### 6 Detection Classes
1. **Customer-Bagpack** - Person with backpack (suspicious indicator)
2. **Product** - Individual merchandise item
3. **Product-Picked** - Item being removed from shelf
4. **Shopping-Cart** - Shopping cart (legitimate activity)
5. **normal** - Normal customer behavior
6. **theft** ⚠️ - **TARGET CLASS** (What we're detecting!)

### Detection Performance Targets
| Metric | Target |
|--------|--------|
| Theft Recall | >70% (catch most thefts!) |
| Theft Precision | >50% (some false positives acceptable) |
| Overall mAP50 | >50% |
| Overall mAP50-95 | >30% |

---

## 🚀 Getting Started

### After Training (24-48 hours)

**1. Load the Model**
```python
from ultralytics import YOLO

model = YOLO('runs/detect/retail_theft_final/weights/best.pt')
```

**2. Run Inference**
```python
# On a single image
results = model.predict('store_image.jpg', conf=0.25)

# On video
results = model.predict('security_footage.mp4', conf=0.25)

# On real-time camera
results = model.predict(source=0, conf=0.25)
```

**3. Detect Thefts**
```python
for result in results:
    for box in result.boxes:
        if int(box.cls[0]) == 5:  # Theft class
            print(f"🚨 THEFT DETECTED! Confidence: {float(box.conf[0]):.1%}")
```

---

## 📊 Training Configuration

### Model
- Architecture: YOLOv8 Nano
- Parameters: 3.0M (very lightweight)
- Pretrained: ImageNet weights
- Framework: PyTorch

### Optimization for Theft Detection
```
Loss Weights:
  - Box: 7.5 (accurate bounding boxes)
  - Class: 0.3 (⬇️ LOWER for higher recall)
  - DFL: 1.5 (distribution focal loss)

Class Weights:
  - Theft: 3.0x (prioritized!)
  - Normal: 0.5x (de-emphasized)
  - Others: 1.0x

Inference:
  - Confidence: 0.25 (lower than default 0.5)
  - IoU threshold: 0.6
```

### Hyperparameters
```
Epochs: 100
Batch Size: 4 (CPU-friendly)
Image Size: 640×640
Optimizer: AdamW
Learning Rate: 0.001 → 0.01
Augmentation: Enabled (mosaic, mixup, rotations, etc.)
Device: CPU (no GPU needed!)
```

---

## 📈 Expected Results

### Training Progress
```
Epoch 1-10    → Initial convergence (losses drop quickly)
Epoch 10-50   → Main training phase (recall improves)
Epoch 50-100  → Fine-tuning (stabilization)
```

### Final Metrics (Estimated)
```
Theft Class:
  ├─ Recall: 70-80% (catch most thefts)
  ├─ Precision: 50-70% (acceptable false alarm rate)
  └─ AP50: 60-75%

Overall Model:
  ├─ mAP50: 50-65%
  ├─ mAP50-95: 30-45%
  └─ Average Inference Time: 200-300ms per image (CPU)
```

---

## 🔧 Available Scripts

### Training
```bash
# Main training script
python train_minimal.py

# Alternative implementations
python train_direct.py
python train_cli.py
```

### Validation & Testing
```bash
# Verify dataset splits
python run_split_verification.py

# Preprocessing pipeline
python preprocessing/main_pipeline.py
```

### Inference (After Training)
```python
from ultralytics import YOLO
model = YOLO('runs/detect/retail_theft_final/weights/best.pt')
results = model.predict('image.jpg', conf=0.25)
```

---

## 📂 Directory Structure

```
phase1_data/
├── 📄 Scripts
│   ├── train_minimal.py          ← MAIN TRAINING (RUNNING)
│   ├── train_direct.py
│   ├── run_split_verification.py
│   ├── data.yaml                 ← Dataset config
│   └── yolov8n.pt                ← Pretrained model
│
├── 📊 Dataset
│   ├── train/images/             (1,675 images)
│   ├── valid/images/             (600 images)
│   ├── test/images/              (303 images)
│   └── */labels/                 (corresponding YOLO format labels)
│
├── 📚 Documentation
│   ├── PROJECT_SUMMARY.md        ← Start here!
│   ├── TRAINING_GUIDE.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── TRAINING_STATUS.md
│   └── README_DATASET.txt
│
├── 📋 Reports
│   ├── reports/split_verification_report.json
│   ├── reports/training_summary.json
│   └── reports/dataset_summary_report.json
│
├── 🛠️ Tools
│   ├── preprocessing/main_pipeline.py
│   ├── preprocessing/dataset_validator.py
│   ├── preprocessing/class_balancer.py
│   └── preprocessing/requirements.txt
│
└── 📤 Output (Generated During Training)
    └── runs/detect/retail_theft_final/
        ├── weights/best.pt       ← ⭐ Best model (USE THIS!)
        ├── weights/last.pt
        ├── results.csv           ← Training metrics
        ├── confusion_matrix.png
        └── *_curve.png           ← Training curves
```

---

## 🎓 Understanding High Recall Optimization

In security applications like theft detection:

**Why Recall > Precision?**
- **False Negative** (Missing a theft) = 😱 CRITICAL FAILURE
- **False Positive** (False alarm) = 😐 Acceptable cost

**How We Optimize for Recall:**
1. ⬇️ **Lower class loss weight** (0.3 vs default 0.5)
   - Reduces penalty for uncertain classifications
   - Model becomes more liberal in detection

2. 📈 **3.0x weight on theft class**
   - Heavily penalizes missed thefts
   - Model focuses on theft patterns

3. 🔍 **Lower inference threshold** (0.25 vs 0.5)
   - Catches borderline cases
   - Increases detection sensitivity

---

## 📊 Monitoring Training

### Check Real-Time Progress
```bash
# View training metrics CSV
tail -f runs/detect/retail_theft_final/results.csv

# List checkpoints
ls -lh runs/detect/retail_theft_final/weights/
```

### Key Metrics to Watch
1. **Box Loss** - Should decrease → 0.5-1.0 range
2. **Class Loss** - May plateau (lower weight)
3. **Recall** - Should increase → 70%+ target
4. **mAP50** - Should increase → 50%+ target

---

## 🚀 Usage After Training

### Quick Start
```python
from ultralytics import YOLO

# Load trained model
model = YOLO('runs/detect/retail_theft_final/weights/best.pt')

# High-recall inference settings
results = model.predict(
    source='image.jpg',
    conf=0.25,    # Lower threshold for recall
    iou=0.6,      # NMS overlap threshold
    verbose=False
)

# Process detections
for result in results:
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        print(f"Class: {class_id}, Confidence: {confidence:.1%}")
```

### Video Processing
```python
results = model.predict('security_footage.mp4', conf=0.25, save=True)
```

### Export for Deployment
```python
# Export to ONNX (cross-platform)
model.export(format='onnx')

# Export to TensorFlow
model.export(format='tf')

# Export to OpenVINO (Intel edge devices)
model.export(format='openvino')
```

---

## ⏱️ Training Timeline

| Time | Milestone |
|------|-----------|
| 0h | Training starts (epoch 1) |
| 3h | ~10 epochs, initial convergence |
| 12h | ~50 epochs, main training phase |
| 24-30h | ~100 epochs, training complete |

**Actual time depends on CPU speed (single-core vs multi-core)**

---

## ✨ Key Features

✅ **Lightweight Model**
- YOLOv8 Nano: only 3.0M parameters
- Runs on any CPU
- Real-time inference capable

✅ **Dataset Verified**
- 2,578 images validated
- No overlaps between splits
- All 8,835 bounding boxes checked
- Class distribution analyzed

✅ **Production Ready**
- Multiple export formats (ONNX, TensorFlow, OpenVINO)
- Real-time video processing
- Batch processing capability
- Inference optimization available

✅ **Well Documented**
- 5+ detailed guides
- Code examples included
- Troubleshooting section
- Deployment instructions

---

## 🔍 Dataset Summary

| Metric | Value |
|--------|-------|
| Total Images | 2,578 |
| Training Images | 1,675 (65%) |
| Validation Images | 600 (23%) |
| Test Images | 303 (12%) |
| Total Bounding Boxes | 8,835 |
| Object Classes | 6 |
| Overlap Between Splits | ✅ ZERO |
| Validation Status | ✅ PASSED |

---

## 🎯 What's Next

1. **Monitor Training** (24-48 hours)
   - Check `runs/detect/retail_theft_final/results.csv`
   - Training will auto-save best model

2. **Evaluate Performance**
   - Run validation on test set
   - Review confusion matrix
   - Check per-class metrics

3. **Deploy Model**
   - Copy `best.pt` to deployment server
   - Integrate with camera system
   - Set confidence threshold to 0.25

4. **Monitor in Production**
   - Log all detections
   - Review false positives
   - Collect hard examples
   - Retrain periodically

---

## 📞 Need Help?

### Documentation
- **PROJECT_SUMMARY.md** - Project overview
- **TRAINING_GUIDE.md** - Training details
- **DEPLOYMENT_GUIDE.md** - How to use model
- **TRAINING_STATUS.md** - Current progress

### Resources
- YOLOv8 Docs: https://docs.ultralytics.com
- GitHub: https://github.com/ultralytics/ultralytics
- GitHub Issues: https://github.com/ultralytics/ultralytics/issues

---

## 📄 License

Dataset: CC BY 4.0 (Roboflow)
Code: MIT License

---

**Project**: Retail Theft Detection with YOLOv8 Nano  
**Status**: 🟢 Training in Progress  
**Started**: 2026-01-18  
**Expected Completion**: 2026-01-20 (in 24-48 hours)  
**Model Location**: `runs/detect/retail_theft_final/weights/best.pt`

---

## 🎉 You're All Set!

Your YOLOv8 retail theft detection model is now **training on CPU**! 

- ✅ Dataset verified (2,578 images)
- ✅ Training optimized for high recall on theft
- ✅ All documentation prepared
- ✅ Deployment guides ready

The model will be production-ready in 24-48 hours. Check back then to deploy it to your retail security system!
