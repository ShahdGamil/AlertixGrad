# Pipeline Architecture Documentation

## System Architecture Overview

This document describes the technical architecture of the YOLO Ensemble Theft Detection Pipeline.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Input: Raw YOLO Dataset                      │
│                  (images/ + labels/ directories)                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Stage 1: VALIDATION                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  - Check YOLO annotation format                        │    │
│  │  - Validate bounding box normalization (0-1)           │    │
│  │  - Detect missing/corrupt/invalid files                │    │
│  │  - Verify class ID ranges                              │    │
│  │  - Auto-fix minor issues                               │    │
│  └────────────────────────────────────────────────────────┘    │
│  Module: src/validation/dataset_validator.py                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Stage 2: CLEANING                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  - Remove corrupt/unreadable images                    │    │
│  │  - Remove invalid bounding boxes (zero area, OOB)      │    │
│  │  - Detect & remove duplicates (perceptual hashing)     │    │
│  │  - Normalize file naming conventions                   │    │
│  │  - Ensure strict image-label pairing                   │    │
│  └────────────────────────────────────────────────────────┘    │
│  Module: src/cleaning/dataset_cleaner.py                        │
│  Output: data/cleaned/                                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Stage 3: BALANCING                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  - Analyze class distribution                          │    │
│  │  - Apply ensemble-aware sampling strategy              │    │
│  │  - Oversample minority classes (Theft, Shopping-Cart)  │    │
│  │  - Undersample majority class (Normal)                 │    │
│  │  - Apply targeted augmentation to minorities           │    │
│  └────────────────────────────────────────────────────────┘    │
│  Module: src/balancing/dataset_balancer.py                      │
│  Output: data/processed/balanced/                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Stage 4: PREPROCESSING                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  - Resize to 640×640 (YOLOv8 standard)                 │    │
│  │  - Letterbox padding (maintain aspect ratio)           │    │
│  │  - Auto-orient images (EXIF metadata)                  │    │
│  │  - Normalize pixel values (optional)                   │    │
│  │  - Convert to efficient training format                │    │
│  └────────────────────────────────────────────────────────┘    │
│  Module: src/preprocessing/preprocessor.py                      │
│  Output: data/processed/preprocessed/                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Stage 5: SPLITTING                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  - Stratified split by class (70/20/10)                │    │
│  │  - Ensure no data leakage across splits                │    │
│  │  - Reproducible (fixed random seed)                    │    │
│  │  - Maintain class balance in each split                │    │
│  └────────────────────────────────────────────────────────┘    │
│  Module: src/splitting/dataset_splitter.py                      │
│  Output: data/train_ready/train/, val/, test/                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Stage 6: VISUALIZATION                          │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  - Generate class distribution plots                   │    │
│  │  - Analyze bounding box statistics                     │    │
│  │  - Image resolution histograms                         │    │
│  │  - Sample grids with annotations                       │    │
│  │  - Train/Val/Test split statistics                     │    │
│  └────────────────────────────────────────────────────────┘    │
│  Module: src/visualization/visualizer.py                        │
│  Output: outputs/visualizations/                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               Stage 7: TRAINING PREPARATION                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  - Generate data.yaml for YOLOv8                       │    │
│  │  - Create model-specific training configs              │    │
│  │  - Generate training scripts (Python, Batch, Shell)    │    │
│  │  - Configure ensemble parameters                       │    │
│  └────────────────────────────────────────────────────────┘    │
│  Module: src/training/ensemble_trainer.py                       │
│  Output: outputs/models/                                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  TRAINING (User-Initiated)                       │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  YOLOv8n  →  Fast inference, baseline performance      │    │
│  │  YOLOv8s  →  Balanced speed/accuracy (recommended)     │    │
│  │  YOLOv8m  →  Maximum accuracy (GPU required)           │    │
│  └────────────────────────────────────────────────────────┘    │
│  Framework: Ultralytics YOLOv8                                  │
│  Output: runs/yolov8*/weights/best.pt                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ENSEMBLE INFERENCE                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Strategy: Weighted Box Fusion (WBF)                   │    │
│  │  - Aggregate predictions from all models               │    │
│  │  - Apply model-specific weights                        │    │
│  │  - Boost Theft class confidence                        │    │
│  │  - Apply NMS with tuned thresholds                     │    │
│  └────────────────────────────────────────────────────────┘    │
│  Library: ensemble-boxes                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Details

### 1. Validation Module
**File:** `src/validation/dataset_validator.py`

**Class:** `YOLODatasetValidator`

**Responsibilities:**
- Validate YOLO annotation format (5 values per line)
- Check bounding box normalization (0-1 range)
- Verify class IDs are within valid range
- Detect corrupt or unreadable images
- Identify missing image-label pairs
- Auto-fix minor bbox issues (clipping, normalization)

**Key Methods:**
```python
validate_dataset(images_dir, labels_dir) -> Dict
_validate_image(img_path) -> (bool, dict)
_validate_label(label_path, img_data) -> (bool, List)
_validate_bbox(x, y, w, h, filename, line) -> (bool, List)
```

**Output:** Validation report with error details

---

### 2. Cleaning Module
**File:** `src/cleaning/dataset_cleaner.py`

**Class:** `YOLODatasetCleaner`

**Responsibilities:**
- Remove corrupt/unreadable images
- Remove invalid bounding boxes (zero area, out of bounds)
- Detect duplicates using perceptual hashing (imagehash)
- Normalize file naming (optional)
- Ensure image-label pairing

**Key Methods:**
```python
clean_dataset(input_imgs, input_lbls, output_imgs, output_lbls) -> Dict
_is_valid_image(img_path) -> bool
_compute_image_hash(img_path) -> str
_clean_label(label_path) -> List[List[float]]
_validate_and_fix_bbox(x, y, w, h) -> (bool, List)
```

**Output:** Cleaned dataset with removed/fixed samples

---

### 3. Balancing Module
**File:** `src/balancing/dataset_balancer.py`

**Class:** `YOLODatasetBalancer`

**Responsibilities:**
- Analyze class distribution
- Apply ensemble-aware balancing strategy
- Oversample minority classes with augmentation
- Undersample majority classes
- Maintain data quality during augmentation

**Key Methods:**
```python
balance_dataset(input_imgs, input_lbls, output_imgs, output_lbls) -> Dict
_analyze_distribution(imgs_dir, lbls_dir) -> Dict[int, List[Path]]
_calculate_target_counts(class_samples) -> Dict[int, int]
_copy_and_augment(img, label, output_dir, augment_pipeline)
```

**Augmentation Pipeline:**
- Horizontal flip (p=0.5)
- Brightness/Contrast (p=0.7)
- Gaussian noise (p=0.3)
- Motion blur (p=0.3)

**Output:** Balanced dataset with class-specific augmentation

---

### 4. Preprocessing Module
**File:** `src/preprocessing/preprocessor.py`

**Class:** `YOLOPreprocessor`

**Responsibilities:**
- Resize images to target size (640×640)
- Apply letterbox padding (maintain aspect ratio)
- Normalize pixel values (optional)
- Auto-orient based on EXIF
- Convert to efficient format (JPEG/PNG)

**Key Methods:**
```python
preprocess_dataset(input_imgs_dir, output_imgs_dir)
preprocess_image(image: np.ndarray) -> np.ndarray
_letterbox_resize(img, target_size, color) -> np.ndarray
```

**Output:** YOLOv8-ready preprocessed images

---

### 5. Splitting Module
**File:** `src/splitting/dataset_splitter.py`

**Class:** `YOLODatasetSplitter`

**Responsibilities:**
- Create stratified train/val/test splits
- Ensure class balance in each split
- Prevent data leakage
- Reproducible splitting (random seed)

**Key Methods:**
```python
split_dataset(input_imgs, input_lbls, output_dir) -> Dict
_stratified_split(samples) -> (train, val, test)
_get_class_distribution(samples) -> Dict[int, int]
```

**Split Ratios:**
- Train: 70%
- Validation: 20%
- Test: 10%

**Output:** Train-ready dataset splits

---

### 6. Visualization Module
**File:** `src/visualization/visualizer.py`

**Class:** `YOLODatasetVisualizer`

**Responsibilities:**
- Generate class distribution plots
- Analyze bounding box statistics (size, aspect ratio)
- Plot image resolution distributions
- Create sample grids with annotations
- Visualize split statistics

**Key Methods:**
```python
generate_all_visualizations(imgs_dir, lbls_dir, split_stats)
plot_class_distribution(lbls_dir)
plot_bbox_statistics(lbls_dir)
plot_sample_grid(imgs_dir, lbls_dir, grid_size)
```

**Output:** PNG visualization files

---

### 7. Training Module
**File:** `src/training/ensemble_trainer.py`

**Class:** `YOLOEnsembleTrainer`

**Responsibilities:**
- Generate YOLOv8 data.yaml
- Create model-specific training configs
- Generate training scripts (Python, Batch, Shell)
- Configure ensemble parameters

**Key Methods:**
```python
prepare_training(dataset_root, output_dir) -> Dict
_generate_data_yaml(dataset_root, output_dir) -> Path
_generate_training_config(model_name, model_info, data_yaml, output_dir) -> Path
_generate_training_scripts(training_configs, output_dir)
```

**Output:** Training-ready configurations and scripts

---

## Utility Modules

### Logger
**File:** `src/utils/logger.py`

**Class:** `PipelineLogger`

**Features:**
- Structured logging (console + file)
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Statistics tracking
- Report generation (JSON, TXT)

### Config Loader
**File:** `src/utils/config_loader.py`

**Class:** `ConfigLoader`

**Features:**
- YAML configuration loading
- Dot-notation access (e.g., `config.get('dataset.classes')`)
- Section-specific getters
- Type-safe configuration access

---

## Pipeline Orchestrator

**File:** `pipeline.py`

**Class:** `YOLOEnsemblePipeline`

**Responsibilities:**
- Initialize all modules
- Execute pipeline stages in sequence
- Handle errors and logging
- Generate final reports

**Key Workflow:**
```python
1. Load configuration
2. Initialize logger and modules
3. Execute stages:
   - Validation
   - Cleaning
   - Balancing
   - Preprocessing
   - Splitting
   - Visualization
   - Training Preparation
4. Generate final summary
5. Save reports (JSON, TXT)
```

---

## Configuration System

**File:** `config/config.yaml`

**Structure:**
```yaml
dataset:           # Dataset info
validation:        # Validation settings
cleaning:          # Cleaning settings
balancing:         # Balancing strategy
preprocessing:     # Preprocessing params
augmentation:      # Augmentation config
splitting:         # Split ratios
yolo_training:     # Training hyperparameters
ensemble:          # Ensemble configuration
visualization:     # Viz settings
logging:           # Logging config
optimization:      # Performance settings
paths:             # Output paths
```

**Key Design Principles:**
- Single source of truth
- Human-readable YAML format
- Comprehensive defaults
- Override flexibility

---

## Data Flow

### File Naming Convention
```
Raw:          img_001.jpg, img_001.txt
Cleaned:      img_000000.jpg, img_000000.txt
Balanced:     Theft_000001.jpg, Theft_000001.txt
Preprocessed: Theft_000001.jpg, Theft_000001.txt
Split:        [same as preprocessed]
```

### Directory Structure
```
data/
├── raw/                    # Input
│   ├── images/
│   └── labels/
├── cleaned/                # After cleaning
│   ├── images/
│   └── labels/
├── processed/
│   ├── balanced/           # After balancing
│   │   ├── images/
│   │   └── labels/
│   └── preprocessed/       # After preprocessing
│       ├── images/
│       └── labels/
└── train_ready/            # Final output
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── val/
    │   ├── images/
    │   └── labels/
    └── test/
        ├── images/
        └── labels/
```

---

## Error Handling Strategy

### Validation Stage
- **Recoverable errors:** Auto-fix and log
- **Unrecoverable errors:** Log and skip sample

### Cleaning Stage
- **Corrupt files:** Remove and log
- **Invalid bboxes:** Fix or remove

### Balancing Stage
- **Augmentation failures:** Fall back to original sample

### Preprocessing Stage
- **Read errors:** Skip and log

### General Strategy
- Continue processing even with errors
- Comprehensive error logging
- Final error summary report

---

## Performance Optimizations

### Implemented:
- ✓ Parallel file reading (multiprocessing)
- ✓ Efficient image hashing (imagehash)
- ✓ Batch processing of augmentations
- ✓ Progress bars (tqdm)
- ✓ Memory-efficient file operations

### Configurable:
- Number of workers
- Cache mode (RAM/disk)
- Batch size
- Image quality

### Future Optimizations:
- GPU-accelerated preprocessing
- Distributed processing
- Streaming data pipeline
- Lazy loading

---

## Testing Strategy

### Unit Tests (Recommended)
```
tests/
├── test_validation.py
├── test_cleaning.py
├── test_balancing.py
├── test_preprocessing.py
├── test_splitting.py
└── test_utils.py
```

### Integration Tests
- Full pipeline execution
- Module interaction testing
- Configuration validation

### Data Quality Tests
- Label format validation
- Bbox boundary checks
- Class ID verification
- Image integrity checks

---

## Deployment Considerations

### Pipeline Deployment
- Dockerize pipeline for reproducibility
- CI/CD for automated testing
- Version control for configs and code

### Model Deployment
- Export to ONNX/TensorRT
- Model serving (TorchServe, TFServing)
- Edge deployment (NVIDIA Jetson)
- API wrapper (FastAPI)

### Monitoring
- Pipeline execution logs
- Data quality metrics
- Training metrics
- Inference performance

---

## Extension Points

### Adding New Augmentations
```python
# In src/balancing/dataset_balancer.py
augment_pipeline = A.Compose([
    # Add new transform here
    A.YourNewTransform(params),
    ...
])
```

### Adding New Validation Rules
```python
# In src/validation/dataset_validator.py
def _validate_custom_rule(self, ...):
    # Your validation logic
    pass
```

### Adding New Visualizations
```python
# In src/visualization/visualizer.py
def plot_custom_analysis(self, ...):
    # Your plotting logic
    pass
```

### Custom Ensemble Strategies
```python
# Create new file: src/training/custom_ensemble.py
class CustomEnsembleMethod:
    def fuse_predictions(self, predictions):
        # Your fusion logic
        pass
```

---

## Dependencies

### Core:
- Python 3.8+
- PyTorch 2.0+
- Ultralytics YOLOv8
- OpenCV
- NumPy

### ML/CV:
- Albumentations (augmentation)
- ensemble-boxes (WBF)
- imagehash (duplicate detection)

### Visualization:
- Matplotlib
- Seaborn
- Plotly (optional)

### Utilities:
- PyYAML (config)
- tqdm (progress)
- pandas (analysis)

---

**Architecture Version:** 1.0
**Last Updated:** 2026-01-19
