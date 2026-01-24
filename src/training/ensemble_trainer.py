"""
Ensemble Training Preparation for YOLO Pipeline
Generates training configurations and data.yaml for multiple YOLO models
"""

import yaml
from pathlib import Path
from typing import Dict, List


class YOLOEnsembleTrainer:
    """Prepare YOLO ensemble training"""

    def __init__(self, logger, config: dict):
        self.logger = logger
        self.config = config

        self.class_names = config.get('classes', [])
        self.models = config.get('models', [])
        self.hyperparams = config.get('hyperparameters', {})

    def prepare_training(self, dataset_root: Path, output_dir: Path) -> Dict:
        """
        Prepare training configurations for ensemble

        Args:
            dataset_root: Root directory containing train/val/test splits
            output_dir: Output directory for training configs

        Returns:
            Training preparation summary
        """
        self.logger.section("Preparing Ensemble Training")

        dataset_root = Path(dataset_root)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate data.yaml
        data_yaml_path = self._generate_data_yaml(dataset_root, output_dir)

        # Generate training configs for each model
        training_configs = {}
        for model_info in self.models:
            if model_info.get('enabled', True):
                model_name = model_info['name']
                config_path = self._generate_training_config(
                    model_name,
                    model_info,
                    data_yaml_path,
                    output_dir
                )
                training_configs[model_name] = str(config_path)

        # Generate training scripts
        self._generate_training_scripts(training_configs, output_dir)

        summary = {
            'data_yaml': str(data_yaml_path),
            'training_configs': training_configs,
            'models_enabled': [m['name'] for m in self.models if m.get('enabled', True)]
        }

        self.logger.success("Ensemble training preparation completed")

        return summary

    def _generate_data_yaml(self, dataset_root: Path, output_dir: Path) -> Path:
        """Generate data.yaml for YOLO training"""

        data_config = {
            'path': str(dataset_root.absolute()),
            'train': 'train/images',
            'val': 'val/images',
            'test': 'test/images',
            'nc': len(self.class_names),
            'names': self.class_names
        }

        output_path = output_dir / 'data.yaml'

        with open(output_path, 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False, sort_keys=False)

        self.logger.info(f"Generated data.yaml: {output_path}")

        return output_path

    def _generate_training_config(
        self,
        model_name: str,
        model_info: Dict,
        data_yaml_path: Path,
        output_dir: Path
    ) -> Path:
        """Generate training configuration for a model"""

        config = {
            'model': model_info.get('pretrained', f"{model_name}.pt"),
            'data': str(data_yaml_path),
            'epochs': self.hyperparams.get('epochs', 100),
            'batch': self.hyperparams.get('batch_size', 16),
            'imgsz': self.hyperparams.get('imgsz', 640),
            'workers': self.hyperparams.get('workers', 4),
            'cache': self.hyperparams.get('cache', 'ram'),
            'optimizer': self.hyperparams.get('optimizer', 'AdamW'),
            'lr0': self.hyperparams.get('lr0', 0.001),
            'lrf': self.hyperparams.get('lrf', 0.01),
            'momentum': self.hyperparams.get('momentum', 0.937),
            'weight_decay': self.hyperparams.get('weight_decay', 0.0005),
            'warmup_epochs': self.hyperparams.get('warmup_epochs', 3),
            'patience': self.hyperparams.get('patience', 20),
            'save': True,
            'project': f'runs/{model_name}',
            'name': 'theft_detection',
            'exist_ok': True,
            'pretrained': True,
            'verbose': True
        }

        output_path = output_dir / f'{model_name}_config.yaml'

        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        self.logger.info(f"Generated config for {model_name}: {output_path}")

        return output_path

    def _generate_training_scripts(
        self,
        training_configs: Dict[str, str],
        output_dir: Path
    ):
        """Generate training scripts for each model"""

        # Python training script
        train_script = self._create_python_training_script(training_configs)
        train_script_path = output_dir / 'train_ensemble.py'

        with open(train_script_path, 'w') as f:
            f.write(train_script)

        self.logger.info(f"Generated training script: {train_script_path}")

        # Batch script for Windows
        batch_script = self._create_batch_training_script(training_configs)
        batch_script_path = output_dir / 'train_ensemble.bat'

        with open(batch_script_path, 'w') as f:
            f.write(batch_script)

        self.logger.info(f"Generated batch script: {batch_script_path}")

        # Shell script for Linux/Mac
        shell_script = self._create_shell_training_script(training_configs)
        shell_script_path = output_dir / 'train_ensemble.sh'

        with open(shell_script_path, 'w') as f:
            f.write(shell_script)

        self.logger.info(f"Generated shell script: {shell_script_path}")

    def _create_python_training_script(self, training_configs: Dict) -> str:
        """Create Python training script"""

        script = """#!/usr/bin/env python3
'''
YOLO Ensemble Training Script
Trains multiple YOLO models for ensemble theft detection
'''

from ultralytics import YOLO
import yaml
from pathlib import Path


def train_model(model_name, config_path):
    '''Train a single YOLO model'''
    print(f'\\n{"="*80}')
    print(f'Training {model_name}')
    print(f'{"="*80}\\n')

    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Initialize model
    model = YOLO(config['model'])

    # Train
    results = model.train(
        data=config['data'],
        epochs=config['epochs'],
        batch=config['batch'],
        imgsz=config['imgsz'],
        workers=config['workers'],
        cache=config['cache'],
        optimizer=config['optimizer'],
        lr0=config['lr0'],
        lrf=config['lrf'],
        momentum=config['momentum'],
        weight_decay=config['weight_decay'],
        warmup_epochs=config['warmup_epochs'],
        patience=config['patience'],
        project=config['project'],
        name=config['name'],
        exist_ok=config['exist_ok'],
        pretrained=config['pretrained'],
        verbose=config['verbose']
    )

    print(f'\\n{model_name} training completed!')
    print(f'Best model: {model.trainer.best}')

    return results


def main():
    '''Train all ensemble models'''
    training_configs = {
"""

        for model_name, config_path in training_configs.items():
            script += f"        '{model_name}': r'{config_path}',\n"

        script += """    }

    results = {}

    for model_name, config_path in training_configs.items():
        try:
            result = train_model(model_name, config_path)
            results[model_name] = 'SUCCESS'
        except Exception as e:
            print(f'ERROR training {model_name}: {e}')
            results[model_name] = f'FAILED: {e}'

    # Print summary
    print('\\n' + '='*80)
    print('ENSEMBLE TRAINING SUMMARY')
    print('='*80)

    for model_name, status in results.items():
        print(f'{model_name}: {status}')


if __name__ == '__main__':
    main()
"""

        return script

    def _create_batch_training_script(self, training_configs: Dict) -> str:
        """Create Windows batch training script"""

        script = "@echo off\n"
        script += "echo ================================================================================\n"
        script += "echo YOLO Ensemble Training - Theft Detection\n"
        script += "echo ================================================================================\n"
        script += "echo.\n\n"

        for model_name in training_configs.keys():
            script += f"echo Training {model_name}...\n"
            script += f"python train_ensemble.py\n"
            script += "echo.\n"

        script += "echo ================================================================================\n"
        script += "echo Training Complete!\n"
        script += "echo ================================================================================\n"
        script += "pause\n"

        return script

    def _create_shell_training_script(self, training_configs: Dict) -> str:
        """Create Linux/Mac shell training script"""

        script = "#!/bin/bash\n\n"
        script += "echo '==============================================================================='\n"
        script += "echo 'YOLO Ensemble Training - Theft Detection'\n"
        script += "echo '==============================================================================='\n"
        script += "echo ''\n\n"

        for model_name in training_configs.keys():
            script += f"echo 'Training {model_name}...'\n"
            script += "python3 train_ensemble.py\n"
            script += "echo ''\n"

        script += "echo '==============================================================================='\n"
        script += "echo 'Training Complete!'\n"
        script += "echo '==============================================================================='\n"

        return script
