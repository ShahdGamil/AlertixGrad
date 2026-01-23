"""
Retail Theft Detection - Dataset Preprocessing Pipeline

This package provides comprehensive preprocessing tools for YOLO format datasets
optimized for retail theft detection with YOLOv8.

Modules:
    - dataset_validator: Validates YOLO labels and images
    - dataset_cleaner: Cleans corrupted and duplicate data
    - class_balancer: Balances class distribution through augmentation
    - visualizer: Generates charts and visual reports
    - yolov8_config: Creates YOLOv8 training configurations
    - main_pipeline: Orchestrates the complete preprocessing workflow
"""

from .dataset_validator import DatasetValidator, validate_dataset
from .dataset_cleaner import DatasetCleaner, clean_dataset
from .class_balancer import ClassBalancer, balance_dataset
from .visualizer import DatasetVisualizer, visualize_dataset
from .yolov8_config import YOLOv8ConfigGenerator, generate_yolov8_configs
from .main_pipeline import RetailTheftPreprocessingPipeline

__version__ = '1.0.0'
__author__ = 'Retail Theft Detection Project'

__all__ = [
    'DatasetValidator',
    'validate_dataset',
    'DatasetCleaner',
    'clean_dataset',
    'ClassBalancer',
    'balance_dataset',
    'DatasetVisualizer',
    'visualize_dataset',
    'YOLOv8ConfigGenerator',
    'generate_yolov8_configs',
    'RetailTheftPreprocessingPipeline'
]
