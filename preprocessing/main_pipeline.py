#!/usr/bin/env python3
"""
Main Preprocessing Pipeline for Retail Theft Detection Dataset
Combines validation, cleaning, balancing, visualization, and YOLOv8 configuration.

Usage:
    python main_pipeline.py [--dataset-path PATH] [--mode cpu|gpu_low|gpu_high]
"""

import os
import sys
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add preprocessing directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dataset_validator import DatasetValidator, ValidationResult
from dataset_cleaner import DatasetCleaner, CleaningResult
from class_balancer import ClassBalancer, BalancingResult
from visualizer import DatasetVisualizer
from yolov8_config import YOLOv8ConfigGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('preprocessing.log')
    ]
)
logger = logging.getLogger(__name__)


class RetailTheftPreprocessingPipeline:
    """
    Complete preprocessing pipeline for retail theft detection dataset.
    Optimized for YOLOv8 Nano training on CPU/limited GPU resources.
    """

    CLASS_NAMES = ['Customer-Bagpack', 'Product', 'Product-Picked',
                   'Shopping-Cart', 'normal', 'theft']
    NUM_CLASSES = 6

    def __init__(self, dataset_path: str, training_mode: str = 'cpu'):
        """
        Initialize preprocessing pipeline.

        Args:
            dataset_path: Path to the dataset root
            training_mode: 'cpu', 'gpu_low', or 'gpu_high'
        """
        self.dataset_path = Path(dataset_path)
        self.training_mode = training_mode
        self.reports_path = self.dataset_path / 'reports'
        self.reports_path.mkdir(exist_ok=True)

        self.pipeline_report = {
            'started_at': datetime.now().isoformat(),
            'dataset_path': str(self.dataset_path),
            'training_mode': training_mode,
            'stages': {}
        }

    def run_full_pipeline(self,
                          skip_validation: bool = False,
                          skip_cleaning: bool = False,
                          skip_balancing: bool = False,
                          skip_visualization: bool = False,
                          skip_config: bool = False) -> Dict[str, Any]:
        """
        Run the complete preprocessing pipeline.

        Args:
            skip_validation: Skip dataset validation
            skip_cleaning: Skip dataset cleaning
            skip_balancing: Skip class balancing
            skip_visualization: Skip visualization generation
            skip_config: Skip YOLOv8 config generation

        Returns:
            Complete pipeline report
        """
        logger.info("=" * 70)
        logger.info("RETAIL THEFT DETECTION - DATASET PREPROCESSING PIPELINE")
        logger.info("=" * 70)
        logger.info(f"Dataset path: {self.dataset_path}")
        logger.info(f"Training mode: {self.training_mode}")
        logger.info("=" * 70)

        # Stage 1: Dataset Validation
        if not skip_validation:
            logger.info("\n[STAGE 1/5] Dataset Validation")
            logger.info("-" * 50)
            validation_result = self._run_validation()
            self.pipeline_report['stages']['validation'] = self._summarize_validation(validation_result)
        else:
            logger.info("\n[STAGE 1/5] Dataset Validation - SKIPPED")

        # Stage 2: Dataset Cleaning
        if not skip_cleaning:
            logger.info("\n[STAGE 2/5] Dataset Cleaning")
            logger.info("-" * 50)
            cleaning_result = self._run_cleaning()
            self.pipeline_report['stages']['cleaning'] = self._summarize_cleaning(cleaning_result)
        else:
            logger.info("\n[STAGE 2/5] Dataset Cleaning - SKIPPED")

        # Stage 3: Class Balancing
        if not skip_balancing:
            logger.info("\n[STAGE 3/5] Class Balancing")
            logger.info("-" * 50)
            balancing_result = self._run_balancing()
            self.pipeline_report['stages']['balancing'] = self._summarize_balancing(balancing_result)
        else:
            logger.info("\n[STAGE 3/5] Class Balancing - SKIPPED")

        # Stage 4: Visualization and Insights
        if not skip_visualization:
            logger.info("\n[STAGE 4/5] Visualization and Insights")
            logger.info("-" * 50)
            viz_files = self._run_visualization()
            self.pipeline_report['stages']['visualization'] = {
                'generated_files': viz_files,
                'output_directory': str(self.reports_path)
            }
        else:
            logger.info("\n[STAGE 4/5] Visualization - SKIPPED")

        # Stage 5: YOLOv8 Configuration
        if not skip_config:
            logger.info("\n[STAGE 5/5] YOLOv8 Configuration")
            logger.info("-" * 50)
            config_files = self._run_config_generation()
            self.pipeline_report['stages']['configuration'] = {
                'generated_files': config_files,
                'training_mode': self.training_mode
            }
        else:
            logger.info("\n[STAGE 5/5] YOLOv8 Configuration - SKIPPED")

        # Finalize report
        self.pipeline_report['completed_at'] = datetime.now().isoformat()
        self.pipeline_report['status'] = 'SUCCESS'

        # Save pipeline report
        report_file = self.reports_path / 'pipeline_report.json'
        with open(report_file, 'w') as f:
            json.dump(self.pipeline_report, f, indent=2, default=str)

        # Print final summary
        self._print_final_summary()

        return self.pipeline_report

    def _run_validation(self) -> ValidationResult:
        """Run dataset validation stage."""
        validator = DatasetValidator(
            str(self.dataset_path),
            num_classes=self.NUM_CLASSES,
            auto_fix=True
        )
        result = validator.validate_all()
        return result

    def _run_cleaning(self) -> CleaningResult:
        """Run dataset cleaning stage."""
        cleaner = DatasetCleaner(
            str(self.dataset_path),
            num_classes=self.NUM_CLASSES,
            remove_duplicates=True,
            duplicate_threshold=5,
            normalize_names=False,  # Keep original names for traceability
            backup=True
        )
        result = cleaner.clean_all()
        return result

    def _run_balancing(self) -> BalancingResult:
        """Run class balancing stage."""
        balancer = ClassBalancer(
            str(self.dataset_path),
            num_classes=self.NUM_CLASSES,
            target_ratio=0.5,  # Target minority classes to be 50% of majority
            max_augmentation_factor=3,  # Max 3x augmentation per image
            seed=42
        )
        result = balancer.balance(strategy='augmentation')

        # Generate balancing report
        balancer.generate_balancing_report(self.reports_path / 'balancing_report.json')

        return result

    def _run_visualization(self) -> List[str]:
        """Run visualization generation stage."""
        visualizer = DatasetVisualizer(
            str(self.dataset_path),
            str(self.reports_path)
        )
        files = visualizer.generate_all_visualizations()
        return files

    def _run_config_generation(self) -> List[str]:
        """Run YOLOv8 configuration generation stage."""
        generator = YOLOv8ConfigGenerator(
            str(self.dataset_path),
            str(self.dataset_path)  # Output configs to dataset root
        )
        files = generator.generate_all_configs()
        return files

    def _summarize_validation(self, result: ValidationResult) -> Dict[str, Any]:
        """Summarize validation results."""
        return {
            'total_images': result.total_images,
            'total_labels': result.total_labels,
            'valid_images': result.valid_images,
            'valid_labels': result.valid_labels,
            'total_bboxes': result.bbox_count,
            'issues': {
                'corrupt_images': len(result.corrupt_images),
                'missing_labels': len(result.missing_labels),
                'missing_images': len(result.missing_images),
                'empty_labels': len(result.empty_labels),
                'invalid_bboxes': len(result.invalid_bboxes),
                'invalid_class_ids': len(result.invalid_class_ids),
                'format_errors': len(result.format_errors)
            },
            'auto_fixed': len(result.fixed_errors),
            'class_distribution': {
                self.CLASS_NAMES[k] if k < len(self.CLASS_NAMES) else f"Class_{k}": v
                for k, v in result.class_counts.items()
            }
        }

    def _summarize_cleaning(self, result: CleaningResult) -> Dict[str, Any]:
        """Summarize cleaning results."""
        return {
            'images_before': result.total_images_before,
            'images_after': result.total_images_after,
            'images_removed': result.total_images_before - result.total_images_after,
            'actions': {
                'corrupt_images_removed': len(result.removed_corrupt_images),
                'invalid_labels_removed': len(result.removed_invalid_labels),
                'duplicates_removed': len(result.removed_duplicates),
                'orphaned_labels_removed': len(result.removed_orphaned_labels),
                'labels_fixed': len(result.fixed_labels)
            }
        }

    def _summarize_balancing(self, result: BalancingResult) -> Dict[str, Any]:
        """Summarize balancing results."""
        return {
            'strategy': result.strategy_used,
            'total_augmented': result.total_augmented,
            'original_distribution': {
                self.CLASS_NAMES[k] if k < len(self.CLASS_NAMES) else f"Class_{k}": v
                for k, v in result.original_class_counts.items()
            },
            'final_distribution': {
                self.CLASS_NAMES[k] if k < len(self.CLASS_NAMES) else f"Class_{k}": v
                for k, v in result.final_class_counts.items()
            },
            'augmented_per_class': {
                self.CLASS_NAMES[k] if k < len(self.CLASS_NAMES) else f"Class_{k}": v
                for k, v in result.augmented_samples.items()
            }
        }

    def _print_final_summary(self):
        """Print final pipeline summary."""
        logger.info("\n" + "=" * 70)
        logger.info("PREPROCESSING PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)

        if 'validation' in self.pipeline_report['stages']:
            val = self.pipeline_report['stages']['validation']
            logger.info(f"\n📊 Dataset Overview:")
            logger.info(f"   Total images: {val['total_images']}")
            logger.info(f"   Total annotations: {val['total_bboxes']}")
            issues_count = sum(val['issues'].values())
            logger.info(f"   Issues found/fixed: {issues_count}")

        if 'cleaning' in self.pipeline_report['stages']:
            clean = self.pipeline_report['stages']['cleaning']
            logger.info(f"\n🧹 Cleaning Results:")
            logger.info(f"   Images removed: {clean['images_removed']}")
            logger.info(f"   Labels fixed: {clean['actions']['labels_fixed']}")

        if 'balancing' in self.pipeline_report['stages']:
            bal = self.pipeline_report['stages']['balancing']
            logger.info(f"\n⚖️  Balancing Results:")
            logger.info(f"   Strategy: {bal['strategy']}")
            logger.info(f"   Augmented samples: {bal['total_augmented']}")

        if 'visualization' in self.pipeline_report['stages']:
            viz = self.pipeline_report['stages']['visualization']
            logger.info(f"\n📈 Visualizations:")
            logger.info(f"   Generated {len(viz['generated_files'])} files")
            logger.info(f"   Output: {viz['output_directory']}")

        if 'configuration' in self.pipeline_report['stages']:
            cfg = self.pipeline_report['stages']['configuration']
            logger.info(f"\n⚙️  YOLOv8 Configuration:")
            logger.info(f"   Training mode: {cfg['training_mode']}")
            logger.info(f"   Generated {len(cfg['generated_files'])} config files")

        logger.info("\n" + "-" * 70)
        logger.info("📁 Output Files:")
        logger.info(f"   • Reports: {self.reports_path}")
        logger.info(f"   • data.yaml: {self.dataset_path / 'data.yaml'}")
        logger.info(f"   • Training script: {self.dataset_path / f'train_yolov8_{self.training_mode}.py'}")
        logger.info(f"   • Pipeline report: {self.reports_path / 'pipeline_report.json'}")

        logger.info("\n" + "-" * 70)
        logger.info("🚀 Next Steps:")
        logger.info(f"   1. Review generated reports in: {self.reports_path}")
        logger.info(f"   2. Check data.yaml configuration")
        logger.info(f"   3. Run training: python train_yolov8_{self.training_mode}.py")
        logger.info("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Retail Theft Detection Dataset Preprocessing Pipeline'
    )
    parser.add_argument(
        '--dataset-path', '-d',
        type=str,
        default='.',
        help='Path to the dataset root (default: current directory)'
    )
    parser.add_argument(
        '--mode', '-m',
        type=str,
        choices=['cpu', 'gpu_low', 'gpu_high'],
        default='cpu',
        help='Training mode for configuration (default: cpu)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip dataset validation stage'
    )
    parser.add_argument(
        '--skip-cleaning',
        action='store_true',
        help='Skip dataset cleaning stage'
    )
    parser.add_argument(
        '--skip-balancing',
        action='store_true',
        help='Skip class balancing stage'
    )
    parser.add_argument(
        '--skip-visualization',
        action='store_true',
        help='Skip visualization generation'
    )
    parser.add_argument(
        '--skip-config',
        action='store_true',
        help='Skip YOLOv8 config generation'
    )

    args = parser.parse_args()

    # Run pipeline
    pipeline = RetailTheftPreprocessingPipeline(
        dataset_path=args.dataset_path,
        training_mode=args.mode
    )

    report = pipeline.run_full_pipeline(
        skip_validation=args.skip_validation,
        skip_cleaning=args.skip_cleaning,
        skip_balancing=args.skip_balancing,
        skip_visualization=args.skip_visualization,
        skip_config=args.skip_config
    )

    return 0 if report['status'] == 'SUCCESS' else 1


if __name__ == '__main__':
    sys.exit(main())
