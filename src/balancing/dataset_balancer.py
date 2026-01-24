"""
Dataset Balancing Module for YOLO Ensemble Pipeline
Handles class imbalance through targeted augmentation and sampling
"""

import cv2
import random
import shutil
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
from tqdm import tqdm
import albumentations as A


class YOLODatasetBalancer:
    """Balance dataset for ensemble training"""

    def __init__(self, logger, config: dict):
        self.logger = logger
        self.config = config

        # Balancing settings
        self.strategy = config.get('strategy', 'ensemble_aware')
        self.class_names = config.get('classes', [])
        self.apply_to_classes = config.get('apply_to_classes', {})

        # Results tracking
        self.results = {
            'original_distribution': {},
            'balanced_distribution': {},
            'augmented_samples': 0,
            'undersampled_samples': 0
        }

    def balance_dataset(
        self,
        input_images_dir: Path,
        input_labels_dir: Path,
        output_images_dir: Path,
        output_labels_dir: Path
    ) -> Dict:
        """
        Balance dataset through augmentation and sampling

        Args:
            input_images_dir: Input images directory
            input_labels_dir: Input labels directory
            output_images_dir: Output images directory
            output_labels_dir: Output labels directory

        Returns:
            Balancing statistics
        """
        self.logger.section("Dataset Balancing")

        # Create output directories
        output_images_dir = Path(output_images_dir)
        output_labels_dir = Path(output_labels_dir)
        output_images_dir.mkdir(parents=True, exist_ok=True)
        output_labels_dir.mkdir(parents=True, exist_ok=True)

        # Analyze class distribution
        class_samples = self._analyze_distribution(
            Path(input_images_dir),
            Path(input_labels_dir)
        )

        self.results['original_distribution'] = {
            self.class_names[k]: v for k, v in class_samples.items()
        }

        # Calculate target counts for each class
        target_counts = self._calculate_target_counts(class_samples)

        # Balance dataset
        self._apply_balancing(
            Path(input_images_dir),
            Path(input_labels_dir),
            output_images_dir,
            output_labels_dir,
            class_samples,
            target_counts
        )

        # Analyze final distribution
        final_distribution = self._analyze_distribution(
            output_images_dir,
            output_labels_dir
        )

        self.results['balanced_distribution'] = {
            self.class_names[k]: v for k, v in final_distribution.items()
        }

        # Generate summary
        summary = self._generate_summary()

        return summary

    def _analyze_distribution(
        self,
        images_dir: Path,
        labels_dir: Path
    ) -> Dict[int, List[Path]]:
        """
        Analyze class distribution in dataset

        Returns:
            Dictionary mapping class_id to list of image paths
        """
        class_samples = defaultdict(list)
        image_files = self._get_image_files(images_dir)

        for img_path in image_files:
            label_path = labels_dir / f"{img_path.stem}.txt"

            if not label_path.exists():
                continue

            # Read label and extract classes
            with open(label_path, 'r') as f:
                lines = f.readlines()

            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    class_samples[class_id].append(img_path)
                    break  # Only count image once per primary class

        return class_samples

    def _calculate_target_counts(
        self,
        class_samples: Dict[int, List[Path]]
    ) -> Dict[int, int]:
        """Calculate target sample counts for each class"""

        current_counts = {k: len(v) for k, v in class_samples.items()}

        # Log current distribution
        self.logger.subsection("Current Class Distribution")
        for class_id, count in current_counts.items():
            class_name = self.class_names[class_id]
            self.logger.info(f"{class_name}: {count}")

        # Calculate target counts based on strategy
        if self.strategy == 'ensemble_aware':
            target_counts = {}

            for class_id, samples in class_samples.items():
                class_name = self.class_names[class_id]
                current_count = len(samples)

                # Check if class has balancing factor
                if class_name in self.apply_to_classes:
                    factor = self.apply_to_classes[class_name]
                    target_counts[class_id] = int(current_count * factor)
                else:
                    target_counts[class_id] = current_count

        else:
            # Standard balancing: match majority class
            max_count = max(len(v) for v in class_samples.values())
            target_counts = {k: max_count for k in class_samples.keys()}

        # Log target distribution
        self.logger.subsection("Target Class Distribution")
        for class_id, count in target_counts.items():
            class_name = self.class_names[class_id]
            self.logger.info(f"{class_name}: {count}")

        return target_counts

    def _apply_balancing(
        self,
        input_images_dir: Path,
        input_labels_dir: Path,
        output_images_dir: Path,
        output_labels_dir: Path,
        class_samples: Dict[int, List[Path]],
        target_counts: Dict[int, int]
    ):
        """Apply balancing through augmentation and undersampling"""

        # Define augmentation pipeline
        augment_pipeline = A.Compose([
            A.HorizontalFlip(p=0.5),
            A.RandomBrightnessContrast(
                brightness_limit=0.2,
                contrast_limit=0.2,
                p=0.7
            ),
            A.GaussNoise(var_limit=(10, 50), p=0.3),
            A.MotionBlur(blur_limit=5, p=0.3),
        ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

        processed_count = 0

        for class_id, samples in class_samples.items():
            class_name = self.class_names[class_id]
            current_count = len(samples)
            target_count = target_counts[class_id]

            self.logger.info(
                f"Processing {class_name}: {current_count} -> {target_count}"
            )

            if target_count >= current_count:
                # Oversample: copy all + augment to reach target
                samples_to_process = samples * (target_count // current_count)
                remaining = target_count - len(samples_to_process)

                if remaining > 0:
                    samples_to_process.extend(
                        random.sample(samples, min(remaining, len(samples)))
                    )

            else:
                # Undersample: randomly select subset
                samples_to_process = random.sample(samples, target_count)
                self.results['undersampled_samples'] += (current_count - target_count)

            # Process samples
            for idx, img_path in enumerate(tqdm(
                samples_to_process,
                desc=f"Balancing {class_name}",
                leave=False
            )):
                label_path = input_labels_dir / f"{img_path.stem}.txt"

                # Determine if augmentation is needed
                if idx >= current_count:
                    # Augment
                    self._copy_and_augment(
                        img_path,
                        label_path,
                        output_images_dir,
                        output_labels_dir,
                        f"{class_name}_{processed_count:06d}",
                        augment_pipeline
                    )
                    self.results['augmented_samples'] += 1
                else:
                    # Just copy
                    self._copy_sample(
                        img_path,
                        label_path,
                        output_images_dir,
                        output_labels_dir,
                        f"{class_name}_{processed_count:06d}"
                    )

                processed_count += 1

    def _copy_sample(
        self,
        img_path: Path,
        label_path: Path,
        output_images_dir: Path,
        output_labels_dir: Path,
        new_stem: str
    ):
        """Copy image and label to output directory"""
        # Copy image
        output_img = output_images_dir / f"{new_stem}{img_path.suffix}"
        shutil.copy2(img_path, output_img)

        # Copy label
        output_label = output_labels_dir / f"{new_stem}.txt"
        shutil.copy2(label_path, output_label)

    def _copy_and_augment(
        self,
        img_path: Path,
        label_path: Path,
        output_images_dir: Path,
        output_labels_dir: Path,
        new_stem: str,
        augment_pipeline
    ):
        """Copy and augment image with labels"""
        # Read image
        image = cv2.imread(str(img_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Read annotations
        bboxes, class_labels = self._read_yolo_labels(label_path)

        if len(bboxes) == 0:
            # No annotations, just copy
            self._copy_sample(
                img_path, label_path,
                output_images_dir, output_labels_dir, new_stem
            )
            return

        try:
            # Apply augmentation
            augmented = augment_pipeline(
                image=image,
                bboxes=bboxes,
                class_labels=class_labels
            )

            aug_image = augmented['image']
            aug_bboxes = augmented['bboxes']
            aug_labels = augmented['class_labels']

            # Save augmented image
            output_img = output_images_dir / f"{new_stem}{img_path.suffix}"
            aug_image_bgr = cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_img), aug_image_bgr)

            # Save augmented labels
            output_label = output_labels_dir / f"{new_stem}.txt"
            self._write_yolo_labels(output_label, aug_bboxes, aug_labels)

        except Exception as e:
            # If augmentation fails, copy original
            self.logger.warning(f"Augmentation failed for {img_path.name}: {e}")
            self._copy_sample(
                img_path, label_path,
                output_images_dir, output_labels_dir, new_stem
            )

    def _read_yolo_labels(self, label_path: Path) -> Tuple[List, List]:
        """Read YOLO format labels"""
        bboxes = []
        class_labels = []

        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    x, y, w, h = map(float, parts[1:5])
                    bboxes.append([x, y, w, h])
                    class_labels.append(class_id)

        return bboxes, class_labels

    def _write_yolo_labels(
        self,
        label_path: Path,
        bboxes: List,
        class_labels: List
    ):
        """Write YOLO format labels"""
        with open(label_path, 'w') as f:
            for bbox, class_id in zip(bboxes, class_labels):
                x, y, w, h = bbox
                f.write(f"{int(class_id)} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

    def _get_image_files(self, images_dir: Path) -> List[Path]:
        """Get all image files"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []

        for ext in image_extensions:
            image_files.extend(images_dir.glob(f'*{ext}'))
            image_files.extend(images_dir.glob(f'*{ext.upper()}'))

        return sorted(image_files)

    def _generate_summary(self) -> Dict:
        """Generate balancing summary"""
        self.logger.subsection("Balancing Summary")

        summary = {
            'original_distribution': self.results['original_distribution'],
            'balanced_distribution': self.results['balanced_distribution'],
            'augmented_samples': self.results['augmented_samples'],
            'undersampled_samples': self.results['undersampled_samples']
        }

        self.logger.info(f"Augmented Samples: {summary['augmented_samples']}")
        self.logger.info(f"Undersampled Samples: {summary['undersampled_samples']}")

        self.logger.success("Dataset balancing completed")

        return summary
