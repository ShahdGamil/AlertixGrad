"""
Dataset Validation Module for YOLO Format Dataset
Validates labels, images, and bounding box formats for retail theft detection.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from PIL import Image
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error."""
    file_path: str
    error_type: str
    message: str
    line_number: Optional[int] = None
    auto_fixable: bool = False


@dataclass
class ValidationResult:
    """Results of dataset validation."""
    total_images: int = 0
    total_labels: int = 0
    valid_images: int = 0
    valid_labels: int = 0
    corrupt_images: List[str] = field(default_factory=list)
    missing_labels: List[str] = field(default_factory=list)
    missing_images: List[str] = field(default_factory=list)
    empty_labels: List[str] = field(default_factory=list)
    invalid_bboxes: List[ValidationError] = field(default_factory=list)
    invalid_class_ids: List[ValidationError] = field(default_factory=list)
    format_errors: List[ValidationError] = field(default_factory=list)
    image_sizes: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    class_counts: Dict[int, int] = field(default_factory=dict)
    bbox_count: int = 0
    fixed_errors: List[str] = field(default_factory=list)


class DatasetValidator:
    """Validates YOLO format dataset for retail theft detection."""

    VALID_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

    def __init__(self, dataset_path: str, num_classes: int = 6, auto_fix: bool = True):
        """
        Initialize validator.

        Args:
            dataset_path: Root path of the dataset
            num_classes: Number of classes in the dataset
            auto_fix: Whether to automatically fix correctable errors
        """
        self.dataset_path = Path(dataset_path)
        self.num_classes = num_classes
        self.auto_fix = auto_fix
        self.result = ValidationResult()

    def validate_all(self) -> ValidationResult:
        """Run all validation checks on the dataset."""
        logger.info("Starting dataset validation...")

        for split in ['train', 'valid', 'test']:
            split_path = self.dataset_path / split
            if split_path.exists():
                logger.info(f"Validating {split} split...")
                self._validate_split(split_path, split)

        self._log_summary()
        return self.result

    def _validate_split(self, split_path: Path, split_name: str):
        """Validate a single split (train/valid/test)."""
        images_path = split_path / 'images'
        labels_path = split_path / 'labels'

        if not images_path.exists():
            logger.warning(f"Images folder not found: {images_path}")
            return
        if not labels_path.exists():
            logger.warning(f"Labels folder not found: {labels_path}")
            return

        # Get all image and label files
        image_files = {f.stem: f for f in images_path.iterdir()
                       if f.suffix.lower() in self.VALID_IMAGE_EXTENSIONS}
        label_files = {f.stem: f for f in labels_path.iterdir()
                       if f.suffix.lower() == '.txt'}

        self.result.total_images += len(image_files)
        self.result.total_labels += len(label_files)

        # Check for missing labels (images without corresponding labels)
        for stem, img_path in image_files.items():
            if stem not in label_files:
                self.result.missing_labels.append(str(img_path))
                if self.auto_fix:
                    # Create empty label file
                    empty_label_path = labels_path / f"{stem}.txt"
                    empty_label_path.touch()
                    self.result.fixed_errors.append(f"Created empty label: {empty_label_path}")

        # Check for orphaned labels (labels without corresponding images)
        for stem, lbl_path in label_files.items():
            if stem not in image_files:
                self.result.missing_images.append(str(lbl_path))

        # Validate each image and its label
        for stem, img_path in image_files.items():
            # Validate image
            is_valid, img_size = self._validate_image(img_path)
            if is_valid:
                self.result.valid_images += 1
                self.result.image_sizes[str(img_path)] = img_size
            else:
                self.result.corrupt_images.append(str(img_path))

            # Validate corresponding label
            if stem in label_files:
                label_path = label_files[stem]
                if self._validate_label(label_path, img_size if is_valid else None):
                    self.result.valid_labels += 1

    def _validate_image(self, image_path: Path) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        Validate a single image file.

        Returns:
            Tuple of (is_valid, (width, height) or None)
        """
        try:
            with Image.open(image_path) as img:
                # Verify the image can be fully loaded
                img.verify()

            # Re-open to get size (verify() closes the file)
            with Image.open(image_path) as img:
                return True, (img.width, img.height)

        except Exception as e:
            logger.error(f"Corrupt image: {image_path} - {e}")
            return False, None

    def _validate_label(self, label_path: Path, img_size: Optional[Tuple[int, int]]) -> bool:
        """
        Validate a single label file.

        Args:
            label_path: Path to the label file
            img_size: Image dimensions (width, height) for bbox validation

        Returns:
            True if label is valid
        """
        is_valid = True

        try:
            content = label_path.read_text().strip()

            # Check for empty files
            if not content:
                self.result.empty_labels.append(str(label_path))
                return True  # Empty labels are valid (no objects)

            lines = content.split('\n')
            fixed_lines = []
            needs_fix = False

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue

                parts = line.split()

                # Check format: class_id x_center y_center width height
                if len(parts) != 5:
                    self.result.format_errors.append(ValidationError(
                        file_path=str(label_path),
                        error_type="format",
                        message=f"Expected 5 values, got {len(parts)}",
                        line_number=line_num,
                        auto_fixable=False
                    ))
                    is_valid = False
                    continue

                try:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])

                    # Validate class ID
                    if class_id < 0 or class_id >= self.num_classes:
                        self.result.invalid_class_ids.append(ValidationError(
                            file_path=str(label_path),
                            error_type="class_id",
                            message=f"Invalid class ID: {class_id} (expected 0-{self.num_classes-1})",
                            line_number=line_num,
                            auto_fixable=False
                        ))
                        is_valid = False
                        continue

                    # Track class counts
                    self.result.class_counts[class_id] = self.result.class_counts.get(class_id, 0) + 1
                    self.result.bbox_count += 1

                    # Validate bounding box coordinates (0-1 range)
                    bbox_valid = True
                    fixed_values = [class_id, x_center, y_center, width, height]

                    for i, (val, name) in enumerate([(x_center, 'x_center'), (y_center, 'y_center'),
                                                      (width, 'width'), (height, 'height')], 1):
                        if val < 0 or val > 1:
                            if self.auto_fix and 0 <= val <= 1.1:  # Small overflow, can fix
                                fixed_values[i] = max(0.0, min(1.0, val))
                                needs_fix = True
                            else:
                                self.result.invalid_bboxes.append(ValidationError(
                                    file_path=str(label_path),
                                    error_type="bbox_range",
                                    message=f"{name}={val} is out of [0,1] range",
                                    line_number=line_num,
                                    auto_fixable=val < 0 or val <= 1.1
                                ))
                                bbox_valid = False
                                is_valid = False

                    # Check if bbox extends beyond image
                    x_min = x_center - width / 2
                    y_min = y_center - height / 2
                    x_max = x_center + width / 2
                    y_max = y_center + height / 2

                    if x_min < 0 or y_min < 0 or x_max > 1 or y_max > 1:
                        if self.auto_fix:
                            # Clip bbox to image bounds
                            x_min = max(0, x_min)
                            y_min = max(0, y_min)
                            x_max = min(1, x_max)
                            y_max = min(1, y_max)
                            fixed_values[1] = (x_min + x_max) / 2
                            fixed_values[2] = (y_min + y_max) / 2
                            fixed_values[3] = x_max - x_min
                            fixed_values[4] = y_max - y_min
                            needs_fix = True

                    # Check for zero or negative dimensions
                    if width <= 0 or height <= 0:
                        self.result.invalid_bboxes.append(ValidationError(
                            file_path=str(label_path),
                            error_type="bbox_dimensions",
                            message=f"Invalid dimensions: width={width}, height={height}",
                            line_number=line_num,
                            auto_fixable=False
                        ))
                        is_valid = False
                        continue

                    fixed_lines.append(f"{fixed_values[0]} {fixed_values[1]:.10f} {fixed_values[2]:.10f} {fixed_values[3]:.10f} {fixed_values[4]:.10f}")

                except ValueError as e:
                    self.result.format_errors.append(ValidationError(
                        file_path=str(label_path),
                        error_type="parse_error",
                        message=f"Failed to parse values: {e}",
                        line_number=line_num,
                        auto_fixable=False
                    ))
                    is_valid = False

            # Write fixed content if needed
            if self.auto_fix and needs_fix and fixed_lines:
                label_path.write_text('\n'.join(fixed_lines))
                self.result.fixed_errors.append(f"Fixed bbox values in: {label_path}")

        except Exception as e:
            self.result.format_errors.append(ValidationError(
                file_path=str(label_path),
                error_type="read_error",
                message=str(e),
                auto_fixable=False
            ))
            is_valid = False

        return is_valid

    def _log_summary(self):
        """Log validation summary."""
        logger.info("=" * 60)
        logger.info("DATASET VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total images: {self.result.total_images}")
        logger.info(f"Total labels: {self.result.total_labels}")
        logger.info(f"Valid images: {self.result.valid_images}")
        logger.info(f"Valid labels: {self.result.valid_labels}")
        logger.info(f"Total bounding boxes: {self.result.bbox_count}")
        logger.info("-" * 60)

        if self.result.corrupt_images:
            logger.warning(f"Corrupt images: {len(self.result.corrupt_images)}")
        if self.result.missing_labels:
            logger.warning(f"Missing labels: {len(self.result.missing_labels)}")
        if self.result.missing_images:
            logger.warning(f"Orphaned labels: {len(self.result.missing_images)}")
        if self.result.empty_labels:
            logger.info(f"Empty labels (background): {len(self.result.empty_labels)}")
        if self.result.invalid_bboxes:
            logger.warning(f"Invalid bboxes: {len(self.result.invalid_bboxes)}")
        if self.result.invalid_class_ids:
            logger.error(f"Invalid class IDs: {len(self.result.invalid_class_ids)}")
        if self.result.format_errors:
            logger.error(f"Format errors: {len(self.result.format_errors)}")
        if self.result.fixed_errors:
            logger.info(f"Auto-fixed issues: {len(self.result.fixed_errors)}")

        logger.info("-" * 60)
        logger.info("Class distribution:")
        class_names = ['Customer-Bagpack', 'Product', 'Product-Picked', 'Shopping-Cart', 'normal', 'theft']
        for class_id, count in sorted(self.result.class_counts.items()):
            name = class_names[class_id] if class_id < len(class_names) else f"Class_{class_id}"
            logger.info(f"  {name} (ID {class_id}): {count}")
        logger.info("=" * 60)


def validate_dataset(dataset_path: str, num_classes: int = 6, auto_fix: bool = True) -> ValidationResult:
    """
    Convenience function to validate a dataset.

    Args:
        dataset_path: Path to the dataset root
        num_classes: Number of classes
        auto_fix: Whether to auto-fix issues

    Returns:
        ValidationResult with all findings
    """
    validator = DatasetValidator(dataset_path, num_classes, auto_fix)
    return validator.validate_all()


if __name__ == "__main__":
    import sys
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "."
    result = validate_dataset(dataset_path)
