"""
Class Balancing and Augmentation Module for YOLO Format Dataset
Handles class imbalance through targeted augmentation for retail theft detection.
"""

import os
import random
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from collections import defaultdict
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class BalancingResult:
    """Results of class balancing."""
    original_class_counts: Dict[int, int] = field(default_factory=dict)
    final_class_counts: Dict[int, int] = field(default_factory=dict)
    augmented_samples: Dict[int, int] = field(default_factory=dict)
    total_augmented: int = 0
    strategy_used: str = ""


class ImageAugmenter:
    """
    Lightweight image augmentation for retail surveillance.
    CPU-optimized and memory-efficient.
    """

    def __init__(self, seed: int = 42):
        """Initialize augmenter with random seed for reproducibility."""
        self.rng = random.Random(seed)
        np.random.seed(seed)

    def horizontal_flip(self, image: Image.Image, bboxes: List[List[float]]) -> Tuple[Image.Image, List[List[float]]]:
        """
        Flip image horizontally.

        Args:
            image: PIL Image
            bboxes: List of [class_id, x_center, y_center, width, height]

        Returns:
            Tuple of (flipped_image, flipped_bboxes)
        """
        flipped = image.transpose(Image.FLIP_LEFT_RIGHT)
        flipped_bboxes = []

        for bbox in bboxes:
            class_id, x_center, y_center, width, height = bbox
            # Flip x coordinate
            new_x_center = 1.0 - x_center
            flipped_bboxes.append([class_id, new_x_center, y_center, width, height])

        return flipped, flipped_bboxes

    def adjust_brightness(self, image: Image.Image, factor_range: Tuple[float, float] = (0.7, 1.3)) -> Image.Image:
        """Randomly adjust brightness."""
        factor = self.rng.uniform(*factor_range)
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    def adjust_contrast(self, image: Image.Image, factor_range: Tuple[float, float] = (0.8, 1.2)) -> Image.Image:
        """Randomly adjust contrast."""
        factor = self.rng.uniform(*factor_range)
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    def add_gaussian_noise(self, image: Image.Image, intensity: float = 0.02) -> Image.Image:
        """Add light Gaussian noise."""
        img_array = np.array(image).astype(np.float32)
        noise = np.random.normal(0, intensity * 255, img_array.shape)
        noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy)

    def motion_blur(self, image: Image.Image, size: int = 3) -> Image.Image:
        """Apply light motion blur."""
        return image.filter(ImageFilter.BoxBlur(size))

    def color_jitter(self, image: Image.Image) -> Image.Image:
        """Apply color jitter (saturation and hue adjustments)."""
        # Saturation
        enhancer = ImageEnhance.Color(image)
        factor = self.rng.uniform(0.8, 1.2)
        image = enhancer.enhance(factor)

        return image

    def random_scale(self, image: Image.Image, bboxes: List[List[float]],
                     scale_range: Tuple[float, float] = (0.9, 1.1)) -> Tuple[Image.Image, List[List[float]]]:
        """
        Random scaling while maintaining aspect ratio.

        Args:
            image: PIL Image
            bboxes: List of bounding boxes
            scale_range: Range for random scaling

        Returns:
            Tuple of (scaled_image, scaled_bboxes)
        """
        scale = self.rng.uniform(*scale_range)

        # Original size
        orig_w, orig_h = image.size

        # New size
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)

        # Resize image
        scaled = image.resize((new_w, new_h), Image.BILINEAR)

        # If scaled down, pad to original size
        if scale < 1.0:
            padded = Image.new('RGB', (orig_w, orig_h), (128, 128, 128))
            offset_x = (orig_w - new_w) // 2
            offset_y = (orig_h - new_h) // 2
            padded.paste(scaled, (offset_x, offset_y))
            scaled = padded

            # Adjust bboxes
            adjusted_bboxes = []
            for bbox in bboxes:
                class_id, x_center, y_center, width, height = bbox
                new_x = (x_center * scale) + (offset_x / orig_w)
                new_y = (y_center * scale) + (offset_y / orig_h)
                new_w_bbox = width * scale
                new_h_bbox = height * scale
                adjusted_bboxes.append([class_id, new_x, new_y, new_w_bbox, new_h_bbox])
            bboxes = adjusted_bboxes

        else:
            # If scaled up, center crop to original size
            offset_x = (new_w - orig_w) // 2
            offset_y = (new_h - orig_h) // 2
            scaled = scaled.crop((offset_x, offset_y, offset_x + orig_w, offset_y + orig_h))

            # Adjust bboxes
            adjusted_bboxes = []
            for bbox in bboxes:
                class_id, x_center, y_center, width, height = bbox
                # Adjust for crop
                new_x = (x_center - offset_x / new_w) / (orig_w / new_w)
                new_y = (y_center - offset_y / new_h) / (orig_h / new_h)
                new_w_bbox = width / (orig_w / new_w)
                new_h_bbox = height / (orig_h / new_h)

                # Clip to valid range
                new_x = max(0, min(1, new_x))
                new_y = max(0, min(1, new_y))
                new_w_bbox = min(new_w_bbox, min(new_x, 1 - new_x) * 2)
                new_h_bbox = min(new_h_bbox, min(new_y, 1 - new_y) * 2)

                if new_w_bbox > 0.01 and new_h_bbox > 0.01:
                    adjusted_bboxes.append([class_id, new_x, new_y, new_w_bbox, new_h_bbox])
            bboxes = adjusted_bboxes

        return scaled, bboxes

    def augment(self, image: Image.Image, bboxes: List[List[float]],
                augmentation_type: str = 'mixed') -> Tuple[Image.Image, List[List[float]]]:
        """
        Apply augmentation based on type.

        Args:
            image: PIL Image
            bboxes: Bounding boxes
            augmentation_type: Type of augmentation to apply

        Returns:
            Tuple of (augmented_image, augmented_bboxes)
        """
        aug_image = image.copy()
        aug_bboxes = [bbox.copy() for bbox in bboxes]

        if augmentation_type == 'flip':
            aug_image, aug_bboxes = self.horizontal_flip(aug_image, aug_bboxes)

        elif augmentation_type == 'brightness':
            aug_image = self.adjust_brightness(aug_image)

        elif augmentation_type == 'contrast':
            aug_image = self.adjust_contrast(aug_image)

        elif augmentation_type == 'noise':
            aug_image = self.add_gaussian_noise(aug_image, intensity=0.015)

        elif augmentation_type == 'blur':
            aug_image = self.motion_blur(aug_image, size=2)

        elif augmentation_type == 'color':
            aug_image = self.color_jitter(aug_image)

        elif augmentation_type == 'scale':
            aug_image, aug_bboxes = self.random_scale(aug_image, aug_bboxes)

        elif augmentation_type == 'mixed':
            # Apply multiple augmentations
            if self.rng.random() < 0.5:
                aug_image, aug_bboxes = self.horizontal_flip(aug_image, aug_bboxes)

            if self.rng.random() < 0.3:
                aug_image = self.adjust_brightness(aug_image)

            if self.rng.random() < 0.3:
                aug_image = self.adjust_contrast(aug_image)

            if self.rng.random() < 0.2:
                aug_image = self.add_gaussian_noise(aug_image, intensity=0.01)

            if self.rng.random() < 0.2:
                aug_image = self.color_jitter(aug_image)

        elif augmentation_type == 'flip_brightness':
            aug_image, aug_bboxes = self.horizontal_flip(aug_image, aug_bboxes)
            aug_image = self.adjust_brightness(aug_image)

        elif augmentation_type == 'flip_contrast':
            aug_image, aug_bboxes = self.horizontal_flip(aug_image, aug_bboxes)
            aug_image = self.adjust_contrast(aug_image)

        return aug_image, aug_bboxes


class ClassBalancer:
    """
    Balances class distribution in YOLO format dataset.
    Focuses on augmenting minority classes (Theft, Shopping-Cart).
    """

    def __init__(self, dataset_path: str, num_classes: int = 6,
                 target_ratio: float = 0.5,
                 max_augmentation_factor: int = 3,
                 seed: int = 42):
        """
        Initialize balancer.

        Args:
            dataset_path: Root path of the dataset
            num_classes: Number of classes
            target_ratio: Target ratio for minority class vs majority class (0.5 = half)
            max_augmentation_factor: Maximum times to augment a single image
            seed: Random seed for reproducibility
        """
        self.dataset_path = Path(dataset_path)
        self.num_classes = num_classes
        self.target_ratio = target_ratio
        self.max_augmentation_factor = max_augmentation_factor
        self.seed = seed
        self.augmenter = ImageAugmenter(seed)
        self.result = BalancingResult()

        # Class names for logging
        self.class_names = ['Customer-Bagpack', 'Product', 'Product-Picked',
                            'Shopping-Cart', 'normal', 'theft']

        # Minority classes that need augmentation
        self.minority_classes = {3, 5}  # Shopping-Cart (3), Theft (5)

    def analyze_distribution(self) -> Dict[int, int]:
        """Analyze class distribution in the training set."""
        class_counts = defaultdict(int)
        images_per_class = defaultdict(list)

        train_labels_path = self.dataset_path / 'train' / 'labels'

        if not train_labels_path.exists():
            logger.error("Training labels not found")
            return {}

        for label_file in train_labels_path.glob('*.txt'):
            content = label_file.read_text().strip()
            if not content:
                continue

            for line in content.split('\n'):
                parts = line.strip().split()
                if len(parts) >= 5:
                    try:
                        class_id = int(parts[0])
                        class_counts[class_id] += 1
                        if label_file.stem not in images_per_class[class_id]:
                            images_per_class[class_id].append(label_file.stem)
                    except ValueError:
                        continue

        self.result.original_class_counts = dict(class_counts)
        self.images_per_class = dict(images_per_class)

        return dict(class_counts)

    def calculate_augmentation_needs(self) -> Dict[int, int]:
        """
        Calculate how many augmented samples are needed for each class.

        Returns:
            Dictionary of class_id -> number of samples to generate
        """
        if not self.result.original_class_counts:
            self.analyze_distribution()

        counts = self.result.original_class_counts
        if not counts:
            return {}

        # Find the majority class count (excluding 'normal' which might dominate)
        max_count = max(counts.values())
        target_count = int(max_count * self.target_ratio)

        augmentation_needs = {}

        for class_id in self.minority_classes:
            current_count = counts.get(class_id, 0)
            if current_count > 0 and current_count < target_count:
                needed = min(target_count - current_count,
                             current_count * self.max_augmentation_factor)
                augmentation_needs[class_id] = needed

        return augmentation_needs

    def balance(self, strategy: str = 'augmentation') -> BalancingResult:
        """
        Balance the dataset using the specified strategy.

        Args:
            strategy: Balancing strategy ('augmentation', 'undersample', 'hybrid')

        Returns:
            BalancingResult with all actions taken
        """
        logger.info("Starting class balancing...")
        self.result.strategy_used = strategy

        # Analyze current distribution
        self.analyze_distribution()
        logger.info("Original class distribution:")
        for class_id, count in sorted(self.result.original_class_counts.items()):
            name = self.class_names[class_id] if class_id < len(self.class_names) else f"Class_{class_id}"
            logger.info(f"  {name}: {count}")

        if strategy == 'augmentation':
            self._balance_with_augmentation()
        elif strategy == 'undersample':
            self._balance_with_undersampling()
        elif strategy == 'hybrid':
            self._balance_with_augmentation()
            # Could add undersampling of majority class here

        # Update final counts
        self._update_final_counts()
        self._log_summary()

        return self.result

    def _balance_with_augmentation(self):
        """Balance by augmenting minority classes."""
        augmentation_needs = self.calculate_augmentation_needs()

        if not augmentation_needs:
            logger.info("No augmentation needed - classes are balanced")
            return

        train_images_path = self.dataset_path / 'train' / 'images'
        train_labels_path = self.dataset_path / 'train' / 'labels'

        # Create augmented subfolder
        aug_images_path = self.dataset_path / 'train' / 'images'
        aug_labels_path = self.dataset_path / 'train' / 'labels'

        # Augmentation types to cycle through
        aug_types = ['flip', 'brightness', 'contrast', 'flip_brightness',
                     'flip_contrast', 'color', 'mixed']

        for class_id, needed_count in augmentation_needs.items():
            class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"Class_{class_id}"
            logger.info(f"Augmenting {class_name}: generating {needed_count} samples...")

            # Get images containing this class
            images_with_class = self.images_per_class.get(class_id, [])
            if not images_with_class:
                continue

            generated = 0
            aug_idx = 0

            while generated < needed_count:
                for img_stem in images_with_class:
                    if generated >= needed_count:
                        break

                    # Find the image file
                    img_path = None
                    for ext in ['.jpg', '.jpeg', '.png']:
                        candidate = train_images_path / f"{img_stem}{ext}"
                        if candidate.exists():
                            img_path = candidate
                            break

                    if not img_path:
                        continue

                    label_path = train_labels_path / f"{img_stem}.txt"
                    if not label_path.exists():
                        continue

                    try:
                        # Load image and labels
                        image = Image.open(img_path).convert('RGB')
                        bboxes = self._read_labels(label_path)

                        # Apply augmentation
                        aug_type = aug_types[aug_idx % len(aug_types)]
                        aug_image, aug_bboxes = self.augmenter.augment(image, bboxes, aug_type)

                        # Save augmented sample
                        aug_name = f"{img_stem}_aug_{class_id}_{generated}"
                        aug_img_path = aug_images_path / f"{aug_name}.jpg"
                        aug_lbl_path = aug_labels_path / f"{aug_name}.txt"

                        aug_image.save(aug_img_path, 'JPEG', quality=95)
                        self._write_labels(aug_lbl_path, aug_bboxes)

                        generated += 1
                        aug_idx += 1

                    except Exception as e:
                        logger.warning(f"Error augmenting {img_stem}: {e}")
                        continue

            self.result.augmented_samples[class_id] = generated
            self.result.total_augmented += generated

    def _balance_with_undersampling(self):
        """Balance by undersampling majority class."""
        # This would move excess samples to a separate folder
        # For now, we focus on augmentation strategy
        pass

    def _read_labels(self, label_path: Path) -> List[List[float]]:
        """Read YOLO format labels."""
        bboxes = []
        content = label_path.read_text().strip()

        if not content:
            return bboxes

        for line in content.split('\n'):
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    bbox = [int(parts[0])] + [float(p) for p in parts[1:5]]
                    bboxes.append(bbox)
                except ValueError:
                    continue

        return bboxes

    def _write_labels(self, label_path: Path, bboxes: List[List[float]]):
        """Write YOLO format labels."""
        lines = []
        for bbox in bboxes:
            class_id = int(bbox[0])
            coords = ' '.join(f"{v:.10f}" for v in bbox[1:])
            lines.append(f"{class_id} {coords}")

        label_path.write_text('\n'.join(lines))

    def _update_final_counts(self):
        """Update final class counts after balancing."""
        class_counts = defaultdict(int)
        train_labels_path = self.dataset_path / 'train' / 'labels'

        for label_file in train_labels_path.glob('*.txt'):
            content = label_file.read_text().strip()
            if not content:
                continue

            for line in content.split('\n'):
                parts = line.strip().split()
                if len(parts) >= 5:
                    try:
                        class_id = int(parts[0])
                        class_counts[class_id] += 1
                    except ValueError:
                        continue

        self.result.final_class_counts = dict(class_counts)

    def _log_summary(self):
        """Log balancing summary."""
        logger.info("=" * 60)
        logger.info("CLASS BALANCING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Strategy used: {self.result.strategy_used}")
        logger.info(f"Total augmented samples: {self.result.total_augmented}")
        logger.info("-" * 60)
        logger.info("Class distribution (before -> after):")

        for class_id in sorted(set(self.result.original_class_counts.keys()) |
                               set(self.result.final_class_counts.keys())):
            name = self.class_names[class_id] if class_id < len(self.class_names) else f"Class_{class_id}"
            before = self.result.original_class_counts.get(class_id, 0)
            after = self.result.final_class_counts.get(class_id, 0)
            aug = self.result.augmented_samples.get(class_id, 0)
            logger.info(f"  {name}: {before} -> {after} (+{aug} augmented)")

        logger.info("=" * 60)

    def get_class_weights(self) -> Dict[int, float]:
        """
        Calculate class weights for weighted loss training.

        Returns:
            Dictionary of class_id -> weight
        """
        counts = self.result.final_class_counts or self.result.original_class_counts
        if not counts:
            self.analyze_distribution()
            counts = self.result.original_class_counts

        total = sum(counts.values())
        num_classes = len(counts)

        weights = {}
        for class_id, count in counts.items():
            # Inverse frequency weighting
            weights[class_id] = total / (num_classes * count) if count > 0 else 1.0

        return weights

    def generate_balancing_report(self, output_path: Optional[Path] = None) -> dict:
        """
        Generate a detailed balancing report.

        Args:
            output_path: Path to save JSON report

        Returns:
            Report dictionary
        """
        report = {
            'strategy': self.result.strategy_used,
            'original_distribution': {
                self.class_names[k] if k < len(self.class_names) else f"Class_{k}": v
                for k, v in self.result.original_class_counts.items()
            },
            'final_distribution': {
                self.class_names[k] if k < len(self.class_names) else f"Class_{k}": v
                for k, v in self.result.final_class_counts.items()
            },
            'augmented_per_class': {
                self.class_names[k] if k < len(self.class_names) else f"Class_{k}": v
                for k, v in self.result.augmented_samples.items()
            },
            'total_augmented': self.result.total_augmented,
            'class_weights': {
                self.class_names[k] if k < len(self.class_names) else f"Class_{k}": round(v, 4)
                for k, v in self.get_class_weights().items()
            },
            'recommendations': self._get_recommendations()
        }

        if output_path:
            output_path.write_text(json.dumps(report, indent=2))
            logger.info(f"Balancing report saved to: {output_path}")

        return report

    def _get_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        counts = self.result.final_class_counts or self.result.original_class_counts
        if not counts:
            return ["Unable to analyze - no data available"]

        max_count = max(counts.values())
        min_count = min(counts.values())

        imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')

        if imbalance_ratio > 10:
            recommendations.append(
                "High class imbalance detected. Consider using focal loss or class weights."
            )

        if counts.get(5, 0) < 500:  # Theft class
            recommendations.append(
                "Theft class has limited samples. Focus augmentation on this class and use high recall threshold."
            )

        if counts.get(3, 0) < 300:  # Shopping-Cart
            recommendations.append(
                "Shopping-Cart class is underrepresented. Consider collecting more data."
            )

        recommendations.append(
            "Use weighted loss with provided class weights for better minority class detection."
        )
        recommendations.append(
            "Enable mosaic augmentation during training for improved generalization."
        )

        return recommendations


def balance_dataset(dataset_path: str, strategy: str = 'augmentation', **kwargs) -> BalancingResult:
    """
    Convenience function to balance a dataset.

    Args:
        dataset_path: Path to the dataset root
        strategy: Balancing strategy
        **kwargs: Additional arguments for ClassBalancer

    Returns:
        BalancingResult with all actions taken
    """
    balancer = ClassBalancer(dataset_path, **kwargs)
    return balancer.balance(strategy)


if __name__ == "__main__":
    import sys
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "."
    result = balance_dataset(dataset_path)
