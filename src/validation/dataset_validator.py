"""
Strict Dataset Validation Module for YOLO Format
Validates YOLO annotation format, bounding boxes, and dataset integrity
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import hashlib


class YOLODatasetValidator:
    """Validates YOLO format dataset with strict checks"""

    def __init__(self, logger, config: dict):
        self.logger = logger
        self.config = config
        self.num_classes = len(config.get('classes', []))

        # Validation settings
        self.strict_mode = config.get('strict_mode', True)
        self.auto_fix = config.get('auto_fix', True)
        self.min_bbox_area = config.get('min_bbox_area', 0.0001)
        self.max_coord = config.get('max_bbox_coord', 1.0)
        self.min_coord = config.get('min_bbox_coord', 0.0)

        # Validation results
        self.results = {
            'total_images': 0,
            'total_labels': 0,
            'valid_images': 0,
            'valid_labels': 0,
            'corrupt_images': [],
            'missing_labels': [],
            'missing_images': [],
            'invalid_labels': [],
            'bbox_errors': defaultdict(list),
            'class_id_errors': [],
            'fixed_labels': [],
            'unrecoverable_errors': []
        }

    def validate_dataset(
        self,
        images_dir: Path,
        labels_dir: Path
    ) -> Dict:
        """
        Perform full dataset validation

        Args:
            images_dir: Directory containing images
            labels_dir: Directory containing labels

        Returns:
            Dictionary containing validation results
        """
        self.logger.section("Dataset Validation")

        images_dir = Path(images_dir)
        labels_dir = Path(labels_dir)

        if not images_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {images_dir}")

        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        image_files = []
        for ext in image_extensions:
            image_files.extend(images_dir.glob(f'*{ext}'))
            image_files.extend(images_dir.glob(f'*{ext.upper()}'))

        self.results['total_images'] = len(image_files)
        self.logger.info(f"Found {len(image_files)} images")

        # Validate each image and its label
        for img_path in image_files:
            self._validate_image_label_pair(img_path, labels_dir)

        # Generate summary
        summary = self._generate_summary()

        return summary

    def _validate_image_label_pair(
        self,
        img_path: Path,
        labels_dir: Path
    ):
        """Validate a single image-label pair"""

        # 1. Validate image file
        img_valid, img_data = self._validate_image(img_path)

        if not img_valid:
            self.results['corrupt_images'].append(str(img_path))
            return

        self.results['valid_images'] += 1

        # 2. Check for corresponding label file
        label_path = labels_dir / f"{img_path.stem}.txt"

        if not label_path.exists():
            self.results['missing_labels'].append(str(img_path))
            self.logger.warning(f"Missing label: {label_path.name}")
            return

        self.results['total_labels'] += 1

        # 3. Validate label file
        label_valid, annotations = self._validate_label(label_path, img_data)

        if label_valid:
            self.results['valid_labels'] += 1

    def _validate_image(self, img_path: Path) -> Tuple[bool, Optional[dict]]:
        """
        Validate image file

        Returns:
            (is_valid, image_data)
        """
        try:
            # Try to read image
            img = cv2.imread(str(img_path))

            if img is None:
                self.logger.error(f"Cannot read image: {img_path.name}")
                return False, None

            height, width = img.shape[:2]

            # Check minimum dimensions
            if height < 32 or width < 32:
                self.logger.error(f"Image too small: {img_path.name} ({width}x{height})")
                return False, None

            img_data = {
                'path': img_path,
                'width': width,
                'height': height,
                'channels': img.shape[2] if len(img.shape) == 3 else 1
            }

            return True, img_data

        except Exception as e:
            self.logger.error(f"Error reading image {img_path.name}: {e}")
            return False, None

    def _validate_label(
        self,
        label_path: Path,
        img_data: dict
    ) -> Tuple[bool, List]:
        """
        Validate YOLO format label file

        YOLO format: class_id x_center y_center width height (all normalized 0-1)

        Returns:
            (is_valid, annotations)
        """
        try:
            with open(label_path, 'r') as f:
                lines = f.readlines()

            if len(lines) == 0:
                self.logger.warning(f"Empty label file: {label_path.name}")
                return True, []  # Empty file is valid (no objects)

            annotations = []
            fixed_annotations = []
            has_errors = False

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue

                parts = line.split()

                # Check format: should have exactly 5 values
                if len(parts) != 5:
                    self.results['invalid_labels'].append(
                        f"{label_path.name}:{line_num} - Invalid format (expected 5 values, got {len(parts)})"
                    )
                    has_errors = True
                    continue

                try:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])

                except ValueError:
                    self.results['invalid_labels'].append(
                        f"{label_path.name}:{line_num} - Cannot parse values"
                    )
                    has_errors = True
                    continue

                # Validate class ID
                if class_id < 0 or class_id >= self.num_classes:
                    self.results['class_id_errors'].append(
                        f"{label_path.name}:{line_num} - Class ID {class_id} out of range [0, {self.num_classes-1}]"
                    )
                    has_errors = True
                    continue

                # Validate normalized coordinates (0-1 range)
                bbox_valid, fixed_bbox = self._validate_bbox(
                    x_center, y_center, width, height,
                    label_path.name, line_num
                )

                if not bbox_valid and not self.auto_fix:
                    has_errors = True
                    continue

                # Use fixed bbox if available
                if fixed_bbox:
                    x_center, y_center, width, height = fixed_bbox
                    self.results['fixed_labels'].append(
                        f"{label_path.name}:{line_num} - Auto-fixed bbox"
                    )

                annotations.append([class_id, x_center, y_center, width, height])
                fixed_annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

            # Auto-fix: rewrite label file if errors were fixed
            if self.auto_fix and len(fixed_annotations) > 0 and len(fixed_annotations) != len(lines):
                with open(label_path, 'w') as f:
                    f.write('\n'.join(fixed_annotations))
                self.logger.info(f"Auto-fixed: {label_path.name}")

            if has_errors and self.strict_mode:
                return False, annotations

            return True, annotations

        except Exception as e:
            self.results['invalid_labels'].append(f"{label_path.name} - Error: {e}")
            return False, []

    def _validate_bbox(
        self,
        x_center: float,
        y_center: float,
        width: float,
        height: float,
        filename: str,
        line_num: int
    ) -> Tuple[bool, Optional[List[float]]]:
        """
        Validate and optionally fix bounding box coordinates

        Returns:
            (is_valid, fixed_bbox or None)
        """
        errors = []
        fixed_bbox = [x_center, y_center, width, height]

        # Check normalization (0-1 range)
        if not (self.min_coord <= x_center <= self.max_coord):
            errors.append(f"x_center={x_center}")
            if self.auto_fix:
                fixed_bbox[0] = max(self.min_coord, min(self.max_coord, x_center))

        if not (self.min_coord <= y_center <= self.max_coord):
            errors.append(f"y_center={y_center}")
            if self.auto_fix:
                fixed_bbox[1] = max(self.min_coord, min(self.max_coord, y_center))

        if not (self.min_coord < width <= self.max_coord):
            errors.append(f"width={width}")
            if self.auto_fix:
                fixed_bbox[2] = max(0.001, min(self.max_coord, width))

        if not (self.min_coord < height <= self.max_coord):
            errors.append(f"height={height}")
            if self.auto_fix:
                fixed_bbox[3] = max(0.001, min(self.max_coord, height))

        # Check minimum area
        area = width * height
        if area < self.min_bbox_area:
            errors.append(f"area={area} (too small)")
            if not self.auto_fix:
                return False, None

        # Check bbox doesn't exceed image boundaries
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center + height / 2

        if x1 < 0 or y1 < 0 or x2 > 1 or y2 > 1:
            errors.append(f"bbox exceeds boundaries")
            if self.auto_fix:
                # Clip to valid range
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(1, x2)
                y2 = min(1, y2)
                fixed_bbox[0] = (x1 + x2) / 2
                fixed_bbox[1] = (y1 + y2) / 2
                fixed_bbox[2] = x2 - x1
                fixed_bbox[3] = y2 - y1

        if errors:
            error_msg = f"{filename}:{line_num} - {', '.join(errors)}"
            self.results['bbox_errors']['all'].append(error_msg)

            if self.auto_fix:
                return True, fixed_bbox
            else:
                return False, None

        return True, None

    def _generate_summary(self) -> Dict:
        """Generate validation summary"""
        self.logger.subsection("Validation Summary")

        total_errors = (
            len(self.results['corrupt_images']) +
            len(self.results['missing_labels']) +
            len(self.results['invalid_labels']) +
            len(self.results['bbox_errors']['all']) +
            len(self.results['class_id_errors'])
        )

        summary = {
            'total_images': self.results['total_images'],
            'valid_images': self.results['valid_images'],
            'corrupt_images': len(self.results['corrupt_images']),
            'total_labels': self.results['total_labels'],
            'valid_labels': self.results['valid_labels'],
            'missing_labels': len(self.results['missing_labels']),
            'invalid_labels': len(self.results['invalid_labels']),
            'bbox_errors': len(self.results['bbox_errors']['all']),
            'class_id_errors': len(self.results['class_id_errors']),
            'fixed_labels': len(self.results['fixed_labels']),
            'total_errors': total_errors,
            'validation_passed': total_errors == 0 or (self.auto_fix and total_errors == len(self.results['fixed_labels']))
        }

        # Log summary
        self.logger.info(f"Total Images: {summary['total_images']}")
        self.logger.info(f"Valid Images: {summary['valid_images']}")
        self.logger.info(f"Corrupt Images: {summary['corrupt_images']}")
        self.logger.info(f"Missing Labels: {summary['missing_labels']}")
        self.logger.info(f"Invalid Labels: {summary['invalid_labels']}")
        self.logger.info(f"Bbox Errors: {summary['bbox_errors']}")
        self.logger.info(f"Class ID Errors: {summary['class_id_errors']}")
        self.logger.info(f"Auto-Fixed: {summary['fixed_labels']}")

        if summary['validation_passed']:
            self.logger.success("Dataset validation PASSED")
        else:
            self.logger.failure("Dataset validation FAILED")

        summary['details'] = self.results

        return summary
