"""
Configuration Loader for YOLO Ensemble Pipeline
Loads and validates YAML configuration files
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """Load and manage pipeline configuration"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_dataset_config(self) -> Dict[str, Any]:
        """Get dataset configuration"""
        return self.config.get('dataset', {})

    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration"""
        return self.config.get('validation', {})

    def get_cleaning_config(self) -> Dict[str, Any]:
        """Get cleaning configuration"""
        return self.config.get('cleaning', {})

    def get_balancing_config(self) -> Dict[str, Any]:
        """Get balancing configuration"""
        return self.config.get('balancing', {})

    def get_preprocessing_config(self) -> Dict[str, Any]:
        """Get preprocessing configuration"""
        return self.config.get('preprocessing', {})

    def get_augmentation_config(self) -> Dict[str, Any]:
        """Get augmentation configuration"""
        return self.config.get('augmentation', {})

    def get_splitting_config(self) -> Dict[str, Any]:
        """Get splitting configuration"""
        return self.config.get('splitting', {})

    def get_yolo_training_config(self) -> Dict[str, Any]:
        """Get YOLO training configuration"""
        return self.config.get('yolo_training', {})

    def get_ensemble_config(self) -> Dict[str, Any]:
        """Get ensemble configuration"""
        return self.config.get('ensemble', {})

    def get_visualization_config(self) -> Dict[str, Any]:
        """Get visualization configuration"""
        return self.config.get('visualization', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config.get('logging', {})

    def get_optimization_config(self) -> Dict[str, Any]:
        """Get optimization configuration"""
        return self.config.get('optimization', {})

    def get_paths_config(self) -> Dict[str, Any]:
        """Get paths configuration"""
        return self.config.get('paths', {})

    def get_class_names(self) -> list:
        """Get class names"""
        return self.config.get('dataset', {}).get('classes', [])

    def get_num_classes(self) -> int:
        """Get number of classes"""
        return len(self.get_class_names())

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access"""
        return self.get(key)

    def __repr__(self) -> str:
        return f"ConfigLoader(config_path='{self.config_path}')"
