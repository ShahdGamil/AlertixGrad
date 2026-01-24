# Usage Guide - YOLO Ensemble Theft Detection Pipeline

## Complete Usage Examples and Best Practices

---

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [Configuration Guide](#configuration-guide)
3. [Pipeline Stages](#pipeline-stages)
4. [Training Models](#training-models)
5. [Analysis & Visualization](#analysis--visualization)
6. [Advanced Scenarios](#advanced-scenarios)

---

## Basic Usage

### Standard Workflow

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Organize your dataset
# Ensure you have:
# - images/ folder with .jpg or .png files
# - labels/ folder with .txt files in YOLO format

# 3. Run the pipeline
python pipeline.py --images data/raw/images --labels data/raw/labels

# 4. Train models
cd outputs/models
python train_ensemble.py

# 5. Analyze results
jupyter notebook analysis_notebook.ipynb
```

---

## Configuration Guide

### Essential Configuration Changes

#### 1. Update Class Names

Edit `config/config.yaml`:

```yaml
dataset:
  classes:
    - "YourClass1"
    - "YourClass2"
    - "YourClass3"

  priority_class: "YourClass1"  # High-recall class
```

#### 2. Adjust Balancing Strategy

```yaml
balancing:
  strategy: "ensemble_aware"
  apply_to_classes:
    YourClass1: 3.0    # Oversample 3x
    YourClass2: 1.0    # Keep as is
    YourClass3: 0.5    # Undersample to 50%
```

#### 3. Tune Training Hyperparameters

```yaml
yolo_training:
  hyperparameters:
    epochs: 150              # Increase for better convergence
    batch_size: 8            # Reduce if OOM errors
    imgsz: 640               # Or 1280 for small objects
    lr0: 0.001               # Learning rate
    patience: 30             # Early stopping patience
```

#### 4. Configure Augmentation

```yaml
augmentation:
  transforms:
    horizontal_flip:
      probability: 0.5       # 50% chance

    brightness_contrast:
      brightness_limit: 0.3  # Increase for more variation
      contrast_limit: 0.3
      probability: 0.8

    mosaic:
      enabled: true
      probability: 0.4       # More mosaic for context
```

---

## Pipeline Stages

### Running Individual Stages

You can run individual pipeline stages programmatically:

#### 1. Validation Only

```python
from src.validation.dataset_validator import YOLODatasetValidator
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

config = ConfigLoader('config/config.yaml')
logger = get_logger()

validator = YOLODatasetValidator(
    logger,
    config.get_validation_config()
)

results = validator.validate_dataset(
    'data/raw/images',
    'data/raw/labels'
)

print(results)
```

#### 2. Cleaning Only

```python
from src.cleaning.dataset_cleaner import YOLODatasetCleaner

cleaner = YOLODatasetCleaner(logger, config.get_cleaning_config())

results = cleaner.clean_dataset(
    'data/raw/images',
    'data/raw/labels',
    'data/cleaned/images',
    'data/cleaned/labels'
)
```

#### 3. Balancing Only

```python
from src.balancing.dataset_balancer import YOLODatasetBalancer

balancer = YOLODatasetBalancer(logger, config.get_balancing_config())

results = balancer.balance_dataset(
    'data/cleaned/images',
    'data/cleaned/labels',
    'data/balanced/images',
    'data/balanced/labels'
)
```

---

## Training Models

### Single Model Training

```python
from ultralytics import YOLO

# Load pretrained model
model = YOLO('yolov8s.pt')

# Train
results = model.train(
    data='outputs/models/data.yaml',
    epochs=100,
    batch=16,
    imgsz=640,
    project='runs/yolov8s',
    name='theft_detection',
    patience=20,
    lr0=0.001,
    cache='ram'
)

# Validate
metrics = model.val()

# Export
model.export(format='onnx')
```

### Ensemble Training

The pipeline generates `train_ensemble.py`. You can customize it:

```python
# outputs/models/train_ensemble.py (generated)

from ultralytics import YOLO
import yaml

def train_model(model_name, config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    model = YOLO(config['model'])

    results = model.train(**config)

    # Save best model
    best_model_path = f"runs/{model_name}/theft_detection/weights/best.pt"
    print(f"Best model saved: {best_model_path}")

    return results

# Train all models
train_model('yolov8n', 'yolov8n_config.yaml')
train_model('yolov8s', 'yolov8s_config.yaml')
```

### Resume Training

```python
from ultralytics import YOLO

# Resume from checkpoint
model = YOLO('runs/yolov8s/theft_detection/weights/last.pt')

results = model.train(resume=True)
```

---

## Analysis & Visualization

### Using the Jupyter Notebook

```bash
# Start Jupyter
jupyter notebook analysis_notebook.ipynb

# The notebook includes:
# - Dataset statistics
# - Class distribution plots
# - Bounding box analysis
# - Sample visualization
# - Training recommendations
```

### Generate Custom Visualizations

```python
from src.visualization.visualizer import YOLODatasetVisualizer

visualizer = YOLODatasetVisualizer(logger, config.get_visualization_config())

# Generate all plots
visualizer.generate_all_visualizations(
    'data/processed/images',
    'data/processed/labels'
)

# Or generate specific plots
visualizer.plot_class_distribution('data/processed/labels')
visualizer.plot_bbox_statistics('data/processed/labels')
visualizer.plot_sample_grid('data/processed/images', 'data/processed/labels')
```

---

## Advanced Scenarios

### Scenario 1: Very Small Dataset (<500 images)

**Configuration adjustments:**

```yaml
balancing:
  minority_oversample_factor: 5.0  # Aggressive oversampling

augmentation:
  transforms:
    horizontal_flip:
      probability: 0.7               # More augmentation

    mosaic:
      probability: 0.6

yolo_training:
  hyperparameters:
    epochs: 200                      # Longer training
    patience: 50                     # More patience
    augment: true                    # Enable all augmentation
```

**Training tips:**
- Use pretrained weights (transfer learning)
- Implement mixup augmentation
- Use smaller models (YOLOv8n, YOLOv8s)
- Monitor validation loss carefully

### Scenario 2: Highly Imbalanced Classes (>10:1 ratio)

**Configuration adjustments:**

```yaml
balancing:
  apply_to_classes:
    MinorityClass: 10.0              # Heavy oversampling
    MajorityClass: 0.3               # Heavy undersampling

yolo_training:
  hyperparameters:
    cls_loss_weight: 1.0             # Increase class loss weight

ensemble:
  class_weights:
    MinorityClass: 2.0               # Boost confidence
```

**Training tips:**
- Use focal loss
- Implement class-weighted sampling
- Monitor per-class metrics
- Lower confidence threshold for minority class

### Scenario 3: Small Objects (<5% of image area)

**Configuration adjustments:**

```yaml
preprocessing:
  target_size: [1280, 1280]          # Higher resolution

yolo_training:
  hyperparameters:
    imgsz: 1280                      # Train at higher resolution
    scale: 0.9                       # More aggressive scaling
```

**Training tips:**
- Use multi-scale training
- Enable mosaic augmentation
- Focus on anchor optimization
- Consider using YOLOv8x for best accuracy

### Scenario 4: Real-Time Inference Required

**Model selection:**

```yaml
yolo_training:
  models:
    - name: "yolov8n"                # Primary model
      enabled: true
    - name: "yolov8s"
      enabled: false                 # Disable for speed
    - name: "yolov8m"
      enabled: false                 # Disable for speed
```

**Optimization:**
- Use YOLOv8n exclusively
- Export to TensorRT or ONNX
- Implement model quantization (FP16/INT8)
- Use smaller input size (416 or 512)
- Batch processing for multiple streams

### Scenario 5: GPU Memory Constraints

**Configuration adjustments:**

```yaml
yolo_training:
  hyperparameters:
    batch_size: 4                    # Reduce batch size
    workers: 2                       # Reduce workers
    cache: false                     # Disable caching
```

**Tips:**
- Use gradient accumulation
- Enable mixed precision training (FP16)
- Train one model at a time
- Use smaller model variants

---

## Performance Tuning

### Hyperparameter Tuning

Use Ultralytics built-in tuning:

```python
from ultralytics import YOLO

model = YOLO('yolov8s.pt')

# Hyperparameter tuning
results = model.tune(
    data='outputs/models/data.yaml',
    epochs=30,
    iterations=100,
    optimizer='AdamW',
    plots=True,
    save=True
)
```

### Anchor Optimization

YOLOv8 uses anchor-free detection, but you can optimize for your dataset:

```python
# Analyze bbox distributions
from src.visualization.visualizer import YOLODatasetVisualizer

visualizer = YOLODatasetVisualizer(logger, config)
visualizer.plot_bbox_statistics('data/processed/labels')

# Adjust model architecture if needed
# (Advanced: requires model modification)
```

### Learning Rate Scheduling

```yaml
yolo_training:
  hyperparameters:
    lr0: 0.01                        # Initial LR
    lrf: 0.01                        # Final LR (lr0 * lrf)
    warmup_epochs: 5                 # Warmup period
```

---

## Monitoring Training

### TensorBoard

```bash
# Launch TensorBoard
tensorboard --logdir runs/

# View at http://localhost:6006
```

### Custom Callbacks

```python
from ultralytics import YOLO

def on_train_epoch_end(trainer):
    # Custom logging
    print(f"Epoch {trainer.epoch}: Loss = {trainer.loss}")

model = YOLO('yolov8s.pt')
model.add_callback('on_train_epoch_end', on_train_epoch_end)

results = model.train(data='data.yaml')
```

---

## Inference & Ensemble

### Single Model Inference

```python
from ultralytics import YOLO

model = YOLO('runs/yolov8s/theft_detection/weights/best.pt')

# Predict on image
results = model.predict(
    source='test_image.jpg',
    conf=0.25,
    iou=0.45,
    save=True
)

# Predict on video
results = model.predict(
    source='test_video.mp4',
    stream=True,
    save=True
)
```

### Ensemble Inference (Weighted Box Fusion)

```python
from ensemble_boxes import weighted_boxes_fusion
from ultralytics import YOLO
import numpy as np

# Load models
models = [
    YOLO('runs/yolov8n/weights/best.pt'),
    YOLO('runs/yolov8s/weights/best.pt'),
    YOLO('runs/yolov8m/weights/best.pt')
]

weights = [0.3, 0.4, 0.3]

# Inference
image = 'test_image.jpg'
all_boxes = []
all_scores = []
all_labels = []

for model in models:
    results = model.predict(image, conf=0.15)

    boxes = results[0].boxes.xyxyn.cpu().numpy()  # Normalized
    scores = results[0].boxes.conf.cpu().numpy()
    labels = results[0].boxes.cls.cpu().numpy()

    all_boxes.append(boxes)
    all_scores.append(scores)
    all_labels.append(labels.astype(int))

# Apply WBF
boxes, scores, labels = weighted_boxes_fusion(
    all_boxes,
    all_scores,
    all_labels,
    weights=weights,
    iou_thr=0.5,
    skip_box_thr=0.01
)

# Boost Theft class confidence
theft_class_id = 5  # Adjust based on your classes
for i, label in enumerate(labels):
    if label == theft_class_id:
        scores[i] *= 1.5  # Boost confidence

print(f"Final detections: {len(boxes)}")
```

---

## Troubleshooting Common Issues

### Issue: Pipeline fails during balancing

**Symptoms:** Memory error or crash during balancing stage

**Solutions:**
1. Reduce oversampling factors
2. Process dataset in batches
3. Disable heavy augmentation temporarily
4. Increase system RAM or use disk-based processing

### Issue: Training loss not decreasing

**Symptoms:** Loss plateaus or increases

**Solutions:**
1. Lower learning rate (lr0=0.0001)
2. Increase warmup epochs
3. Check data quality and labels
4. Reduce augmentation intensity
5. Try different optimizer (SGD vs AdamW)

### Issue: Low recall on priority class

**Symptoms:** Missing detections for Theft class

**Solutions:**
1. Increase oversampling factor to 5.0+
2. Lower confidence threshold to 0.10
3. Increase class weight to 2.0+
4. Add more augmentation for that class
5. Use focal loss

### Issue: High false positive rate

**Symptoms:** Too many incorrect detections

**Solutions:**
1. Increase confidence threshold
2. Add hard negative mining
3. Balance dataset better
4. Reduce augmentation
5. Train longer for better convergence

---

## Best Practices

### Data Quality
- ✅ Manually review 10% of annotations
- ✅ Check for label consistency
- ✅ Verify class definitions are clear
- ✅ Remove ambiguous samples

### Training
- ✅ Always use pretrained weights
- ✅ Monitor val loss, not train loss
- ✅ Save checkpoints frequently
- ✅ Use early stopping
- ✅ Track experiments (MLflow, W&B)

### Validation
- ✅ Use stratified test set
- ✅ Test on real-world scenarios
- ✅ Analyze failure cases
- ✅ Measure per-class performance
- ✅ Consider edge cases

### Deployment
- ✅ Benchmark on target hardware
- ✅ Implement confidence thresholds
- ✅ Add post-processing
- ✅ Monitor production performance
- ✅ Prepare model rollback

---

## Additional Resources

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [Ensemble Methods Paper](https://arxiv.org/abs/1910.13302)
- [Class Imbalance Handling](https://arxiv.org/abs/1708.02002)

---

**Questions? Check the main README.md or open an issue.**
