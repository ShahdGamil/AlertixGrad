"""
YOLOv8 Configuration Module
Generates data.yaml, training configs, and optimization recommendations for retail theft detection.
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """YOLOv8 training configuration."""
    # Model
    model: str = 'yolov8n.pt'
    pretrained: bool = True

    # Data
    data: str = 'data.yaml'
    imgsz: int = 640
    cache: str = 'ram'  # 'ram', 'disk', or False

    # Training hyperparameters
    epochs: int = 100
    batch: int = 8  # CPU-friendly
    workers: int = 4
    patience: int = 50  # Early stopping patience

    # Optimizer
    optimizer: str = 'AdamW'
    lr0: float = 0.001
    lrf: float = 0.01  # Final learning rate factor
    momentum: float = 0.937
    weight_decay: float = 0.0005
    warmup_epochs: float = 3.0
    warmup_momentum: float = 0.8
    warmup_bias_lr: float = 0.1

    # Loss weights
    box: float = 7.5
    cls: float = 0.5
    dfl: float = 1.5

    # Augmentation (lightweight for CPU)
    hsv_h: float = 0.015
    hsv_s: float = 0.7
    hsv_v: float = 0.4
    degrees: float = 0.0
    translate: float = 0.1
    scale: float = 0.5
    shear: float = 0.0
    perspective: float = 0.0
    flipud: float = 0.0
    fliplr: float = 0.5
    mosaic: float = 1.0
    mixup: float = 0.0
    copy_paste: float = 0.0

    # Device
    device: str = 'cpu'  # or 'cuda:0', '0', etc.

    # Other
    project: str = 'runs/detect'
    name: str = 'retail_theft'
    exist_ok: bool = True
    pretrained: bool = True
    verbose: bool = True
    seed: int = 42
    deterministic: bool = True
    single_cls: bool = False
    rect: bool = False
    cos_lr: bool = False
    close_mosaic: int = 10
    resume: bool = False
    amp: bool = True
    fraction: float = 1.0
    profile: bool = False
    freeze: Optional[int] = None
    multi_scale: bool = False
    overlap_mask: bool = True
    mask_ratio: int = 4
    dropout: float = 0.0
    val: bool = True
    save: bool = True
    save_period: int = -1
    plots: bool = True


class YOLOv8ConfigGenerator:
    """
    Generates YOLOv8-compatible configuration files and training recommendations.
    Optimized for retail theft detection on CPU/limited GPU resources.
    """

    CLASS_NAMES = ['Customer-Bagpack', 'Product', 'Product-Picked',
                   'Shopping-Cart', 'normal', 'theft']

    def __init__(self, dataset_path: str, output_path: Optional[str] = None):
        """
        Initialize config generator.

        Args:
            dataset_path: Root path of the dataset
            output_path: Path for output configs (default: dataset_path)
        """
        self.dataset_path = Path(dataset_path)
        self.output_path = Path(output_path) if output_path else self.dataset_path
        self.config = TrainingConfig()

    def generate_data_yaml(self, absolute_paths: bool = False) -> str:
        """
        Generate YOLOv8-compatible data.yaml file.

        Args:
            absolute_paths: Whether to use absolute paths

        Returns:
            Path to generated data.yaml
        """
        if absolute_paths:
            train_path = str(self.dataset_path / 'train' / 'images')
            val_path = str(self.dataset_path / 'valid' / 'images')
            test_path = str(self.dataset_path / 'test' / 'images')
        else:
            train_path = 'train/images'
            val_path = 'valid/images'
            test_path = 'test/images'

        data_config = {
            'path': str(self.dataset_path.absolute()) if absolute_paths else '.',
            'train': train_path,
            'val': val_path,
            'test': test_path,
            'nc': len(self.CLASS_NAMES),
            'names': self.CLASS_NAMES
        }

        output_file = self.output_path / 'data.yaml'
        with open(output_file, 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Generated data.yaml at: {output_file}")
        return str(output_file)

    def generate_training_config(self, mode: str = 'cpu') -> Dict[str, Any]:
        """
        Generate training configuration based on hardware mode.

        Args:
            mode: 'cpu', 'gpu_low', 'gpu_high'

        Returns:
            Training configuration dictionary
        """
        config = self.config

        if mode == 'cpu':
            config.device = 'cpu'
            config.batch = 4  # Small batch for CPU
            config.workers = 2
            config.cache = 'disk'  # Disk cache to save RAM
            config.imgsz = 640
            config.epochs = 100
            config.mosaic = 0.5  # Reduced mosaic for speed
            config.mixup = 0.0
            config.amp = False  # Disable mixed precision on CPU
            config.multi_scale = False

        elif mode == 'gpu_low':
            config.device = '0'
            config.batch = 8
            config.workers = 4
            config.cache = 'ram'
            config.imgsz = 640
            config.epochs = 150
            config.mosaic = 1.0
            config.mixup = 0.1
            config.amp = True

        elif mode == 'gpu_high':
            config.device = '0'
            config.batch = 16
            config.workers = 8
            config.cache = 'ram'
            config.imgsz = 640
            config.epochs = 200
            config.mosaic = 1.0
            config.mixup = 0.15
            config.amp = True
            config.multi_scale = True

        # Convert to dict
        config_dict = {
            'model': config.model,
            'data': str(self.output_path / 'data.yaml'),
            'imgsz': config.imgsz,
            'epochs': config.epochs,
            'batch': config.batch,
            'workers': config.workers,
            'cache': config.cache,
            'device': config.device,
            'patience': config.patience,
            'optimizer': config.optimizer,
            'lr0': config.lr0,
            'lrf': config.lrf,
            'momentum': config.momentum,
            'weight_decay': config.weight_decay,
            'warmup_epochs': config.warmup_epochs,
            'warmup_momentum': config.warmup_momentum,
            'warmup_bias_lr': config.warmup_bias_lr,
            'box': config.box,
            'cls': config.cls,
            'dfl': config.dfl,
            'hsv_h': config.hsv_h,
            'hsv_s': config.hsv_s,
            'hsv_v': config.hsv_v,
            'degrees': config.degrees,
            'translate': config.translate,
            'scale': config.scale,
            'shear': config.shear,
            'perspective': config.perspective,
            'flipud': config.flipud,
            'fliplr': config.fliplr,
            'mosaic': config.mosaic,
            'mixup': config.mixup,
            'copy_paste': config.copy_paste,
            'project': config.project,
            'name': config.name,
            'exist_ok': config.exist_ok,
            'pretrained': config.pretrained,
            'verbose': config.verbose,
            'seed': config.seed,
            'deterministic': config.deterministic,
            'single_cls': config.single_cls,
            'rect': config.rect,
            'cos_lr': config.cos_lr,
            'close_mosaic': config.close_mosaic,
            'amp': config.amp,
            'val': config.val,
            'save': config.save,
            'plots': config.plots
        }

        # Save config
        config_file = self.output_path / f'training_config_{mode}.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Generated training config at: {config_file}")
        return config_dict

    def generate_training_script(self, mode: str = 'cpu') -> str:
        """
        Generate a Python training script.

        Args:
            mode: Hardware mode

        Returns:
            Path to generated script
        """
        config = self.generate_training_config(mode)

        script = f'''#!/usr/bin/env python3
"""
YOLOv8 Nano Training Script for Retail Theft Detection
Generated for {mode.upper()} training mode.

Usage:
    python train_yolov8.py
"""

from ultralytics import YOLO
import torch
import os

# Set working directory
os.chdir(r"{self.dataset_path.absolute()}")

# Check device
device = "{config['device']}"
if device != 'cpu':
    if not torch.cuda.is_available():
        print("CUDA not available, falling back to CPU")
        device = 'cpu'
    else:
        print(f"Using GPU: {{torch.cuda.get_device_name(0)}}")
else:
    print("Training on CPU - this will be slower but works")

# Load model
model = YOLO("{config['model']}")

# Training arguments optimized for retail theft detection
results = model.train(
    # Data
    data=r"{config['data']}",
    imgsz={config['imgsz']},
    cache="{config['cache']}",

    # Training
    epochs={config['epochs']},
    batch={config['batch']},
    workers={config['workers']},
    device=device,
    patience={config['patience']},

    # Optimizer
    optimizer="{config['optimizer']}",
    lr0={config['lr0']},
    lrf={config['lrf']},
    momentum={config['momentum']},
    weight_decay={config['weight_decay']},
    warmup_epochs={config['warmup_epochs']},
    warmup_momentum={config['warmup_momentum']},
    warmup_bias_lr={config['warmup_bias_lr']},

    # Loss weights
    box={config['box']},
    cls={config['cls']},
    dfl={config['dfl']},

    # Augmentation
    hsv_h={config['hsv_h']},
    hsv_s={config['hsv_s']},
    hsv_v={config['hsv_v']},
    degrees={config['degrees']},
    translate={config['translate']},
    scale={config['scale']},
    shear={config['shear']},
    perspective={config['perspective']},
    flipud={config['flipud']},
    fliplr={config['fliplr']},
    mosaic={config['mosaic']},
    mixup={config['mixup']},
    copy_paste={config['copy_paste']},

    # Project settings
    project="{config['project']}",
    name="{config['name']}",
    exist_ok={config['exist_ok']},
    pretrained={config['pretrained']},
    verbose={config['verbose']},
    seed={config['seed']},
    deterministic={config['deterministic']},
    single_cls={config['single_cls']},
    rect={config['rect']},
    cos_lr={config['cos_lr']},
    close_mosaic={config['close_mosaic']},
    amp={config['amp']},
    val={config['val']},
    save={config['save']},
    plots={config['plots']}
)

print("\\nTraining completed!")
print(f"Best model saved at: {{results.save_dir}}/weights/best.pt")
print(f"Results saved at: {{results.save_dir}}")

# Validation on test set
print("\\nRunning validation on test set...")
metrics = model.val(data=r"{config['data']}", split='test')
print(f"Test mAP50: {{metrics.box.map50:.4f}}")
print(f"Test mAP50-95: {{metrics.box.map:.4f}}")

# Per-class metrics
print("\\nPer-class AP50:")
class_names = {self.CLASS_NAMES}
for i, name in enumerate(class_names):
    if i < len(metrics.box.ap50):
        print(f"  {{name}}: {{metrics.box.ap50[i]:.4f}}")
'''

        script_file = self.output_path / f'train_yolov8_{mode}.py'
        with open(script_file, 'w') as f:
            f.write(script)

        logger.info(f"Generated training script at: {script_file}")
        return str(script_file)

    def generate_inference_script(self) -> str:
        """Generate an inference script for the trained model."""
        script = f'''#!/usr/bin/env python3
"""
YOLOv8 Inference Script for Retail Theft Detection

Usage:
    python inference.py --source path/to/image_or_video
    python inference.py --source 0  # webcam
"""

import argparse
from ultralytics import YOLO
import cv2
import os

# Class names
CLASS_NAMES = {self.CLASS_NAMES}

# Class colors (BGR)
CLASS_COLORS = {{
    0: (0, 0, 255),      # Customer-Bagpack - Red
    1: (0, 255, 0),      # Product - Green
    2: (255, 0, 0),      # Product-Picked - Blue
    3: (255, 255, 0),    # Shopping-Cart - Cyan
    4: (255, 0, 255),    # normal - Magenta
    5: (0, 165, 255),    # theft - Orange (highlight)
}}

def run_inference(
    model_path: str,
    source: str,
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
    save_output: bool = True,
    show: bool = True
):
    """Run inference on source."""
    # Load model
    model = YOLO(model_path)

    # Run inference
    results = model.predict(
        source=source,
        conf=conf_threshold,
        iou=iou_threshold,
        save=save_output,
        show=show,
        stream=True  # For videos/webcam
    )

    # Process results
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else f"Class_{{cls_id}}"

                # Alert for theft detection
                if cls_id == 5:  # Theft class
                    print(f"[ALERT] THEFT DETECTED! Confidence: {{conf:.2f}}")

                print(f"Detected: {{class_name}} ({{conf:.2f}})")

    print("\\nInference complete!")


def main():
    parser = argparse.ArgumentParser(description='YOLOv8 Retail Theft Detection Inference')
    parser.add_argument('--model', type=str, default='runs/detect/retail_theft/weights/best.pt',
                        help='Path to trained model')
    parser.add_argument('--source', type=str, required=True,
                        help='Source (image, video, or camera index)')
    parser.add_argument('--conf', type=float, default=0.25,
                        help='Confidence threshold')
    parser.add_argument('--iou', type=float, default=0.45,
                        help='IoU threshold for NMS')
    parser.add_argument('--save', action='store_true',
                        help='Save output')
    parser.add_argument('--no-show', action='store_true',
                        help='Do not display output')

    args = parser.parse_args()

    run_inference(
        model_path=args.model,
        source=args.source,
        conf_threshold=args.conf,
        iou_threshold=args.iou,
        save_output=args.save,
        show=not args.no_show
    )


if __name__ == '__main__':
    main()
'''

        script_file = self.output_path / 'inference.py'
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script)

        logger.info(f"Generated inference script at: {script_file}")
        return str(script_file)

    def generate_optimization_recommendations(self) -> Dict[str, Any]:
        """Generate performance optimization recommendations."""
        recommendations = {
            'model_selection': {
                'recommended': 'yolov8n.pt',
                'reason': 'Nano model is optimal for CPU/limited GPU training',
                'alternatives': {
                    'yolov8s.pt': 'If GPU memory > 4GB, provides better accuracy',
                    'yolov8m.pt': 'If GPU memory > 8GB, significantly better accuracy'
                }
            },
            'image_size': {
                'recommended': 640,
                'cpu_alternative': 416,
                'note': 'Use 416 for faster CPU training, 640 for better small object detection'
            },
            'batch_size': {
                'cpu': {'batch': 4, 'reason': 'Small batches prevent memory issues'},
                'gpu_4gb': {'batch': 8, 'reason': 'Safe for 4GB VRAM with YOLOv8n'},
                'gpu_8gb': {'batch': 16, 'reason': 'Optimal for 8GB VRAM'},
                'gpu_16gb+': {'batch': 32, 'reason': 'Maximum efficiency'}
            },
            'learning_rate': {
                'default': 0.001,
                'fine_tuning': 0.0001,
                'note': 'Lower LR if training is unstable'
            },
            'class_imbalance_handling': {
                'strategy': 'weighted_loss',
                'cls_weight': 1.0,  # Increase for minority classes
                'focal_loss': {
                    'gamma': 2.0,
                    'note': 'Helps with hard examples and minority classes'
                },
                'oversampling': 'Applied to Theft and Shopping-Cart classes'
            },
            'augmentation_settings': {
                'cpu_optimized': {
                    'mosaic': 0.5,
                    'mixup': 0.0,
                    'copy_paste': 0.0,
                    'note': 'Reduced augmentation for faster training'
                },
                'gpu_full': {
                    'mosaic': 1.0,
                    'mixup': 0.15,
                    'copy_paste': 0.1,
                    'note': 'Full augmentation for better generalization'
                }
            },
            'early_stopping': {
                'patience': 50,
                'monitor': 'val/mAP50',
                'note': 'Stop if no improvement for 50 epochs'
            },
            'transfer_learning': {
                'strategy': 'Full fine-tuning from COCO pretrained weights',
                'freeze_backbone': False,
                'note': 'YOLOv8n.pt provides good initialization for retail objects'
            },
            'theft_detection_optimization': {
                'conf_threshold': 0.25,
                'iou_threshold': 0.45,
                'note': 'Lower confidence for high recall on theft detection'
            },
            'memory_optimization': {
                'cache': 'disk',  # For CPU
                'workers': 2,
                'pin_memory': False,
                'note': 'Disk caching saves RAM, essential for CPU training'
            }
        }

        # Save recommendations
        output_file = self.output_path / 'optimization_recommendations.json'
        with open(output_file, 'w') as f:
            json.dump(recommendations, f, indent=2)

        logger.info(f"Generated optimization recommendations at: {output_file}")
        return recommendations

    def generate_all_configs(self) -> List[str]:
        """Generate all configuration files."""
        generated_files = []

        # Generate data.yaml
        generated_files.append(self.generate_data_yaml(absolute_paths=True))

        # Generate training configs for different modes
        for mode in ['cpu', 'gpu_low', 'gpu_high']:
            self.generate_training_config(mode)
            generated_files.append(str(self.output_path / f'training_config_{mode}.yaml'))
            generated_files.append(self.generate_training_script(mode))

        # Generate inference script
        generated_files.append(self.generate_inference_script())

        # Generate optimization recommendations
        self.generate_optimization_recommendations()
        generated_files.append(str(self.output_path / 'optimization_recommendations.json'))

        return generated_files


def generate_yolov8_configs(dataset_path: str, output_path: Optional[str] = None) -> List[str]:
    """
    Convenience function to generate all YOLOv8 configs.

    Args:
        dataset_path: Path to the dataset root
        output_path: Optional output path

    Returns:
        List of generated file paths
    """
    generator = YOLOv8ConfigGenerator(dataset_path, output_path)
    return generator.generate_all_configs()


if __name__ == "__main__":
    import sys
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "."
    files = generate_yolov8_configs(dataset_path)
    print(f"Generated {len(files)} config files")
