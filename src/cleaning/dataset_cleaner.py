"""
Dataset Cleaning Module for YOLO Ensemble Pipeline
Removes corrupt images, invalid labels, duplicates, and normalizes dataset
"""

import cv2
import shutil
import hashlib
import imagehash
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from tqdm import tqdm


class YOLODatasetCleaner:
    """Clean and normalize YOLO dataset"""

    def __init__(self, logger, config: dict):
        self.logger = logger
        self.config = config
        self.num_classes = len(config.get('classes', []))

        # Cleaning settings
        self.remove_corrupt = config.get('remove_corrupt_images', True)
        self.remove_invalid_bbox = config.get('remove_invalid_bboxes', True)
        self.remove_duplicates = config.get('remove_duplicates', True)
        self.normalize_names = config.get('normalize_filenames', True)
        self.hash_algorithm = config.get('hash_algorithm', 'md5')
        self.min_image_size = tuple(config.get('min_image_size', [32, 32]))

        # Cleaning results
        self.results = {
            'total_processed': 0,
            'removed_corrupt': 0,
            'removed_invalid_labels': 0,
            'removed_duplicates': 0,
            'removed_no_labels': 0,
            'fixed_bboxes': 0,
            'renamed_files': 0,
            'final_count': 0
        }

    def clean_dataset(
        self,
        input_images_dir: Path,
        input_labels_dir: Path,
        output_images_dir: Path,
        output_labels_dir: Path
    ) -> Dict:
        """
        Clean dataset and save to output directory

        Args:
            input_images_dir: Input images directory
            input_labels_dir: Input labels directory
            output_images_dir: Output images directory
            output_labels_dir: Output labels directory

        Returns:
            Cleaning statistics
        """
        self.logger.section("Dataset Cleaning")

        # Create output directories
        output_images_dir = Path(output_images_dir)
        output_labels_dir = Path(output_labels_dir)
        output_images_dir.mkdir(parents=True, exist_ok=True)
        output_labels_dir.mkdir(parents=True, exist_ok=True)

        # Get all image files
        image_files = self._get_image_files(Path(input_images_dir))
        self.results['total_processed'] = len(image_files)

        self.logger.info(f"Processing {len(image_files)} images")

        # Track duplicates using image hashing
        seen_hashes: Set[str] = set()
        processed_count = 0

        # Process each image
        for img_path in tqdm(image_files, desc="Cleaning dataset"):
            # Check if image is valid
            if not self._is_valid_image(img_path):
                self.results['removed_corrupt'] += 1
                continue

            # Check for duplicates
            if self.remove_duplicates:
                img_hash = self._compute_image_hash(img_path)
                if img_hash in seen_hashes:
                    self.results['removed_duplicates'] += 1
                    continue
                seen_hashes.add(img_hash)

            # Check for corresponding label
            label_path = Path(input_labels_dir) / f"{img_path.stem}.txt"

            if not label_path.exists():
                self.results['removed_no_labels'] += 1
                continue

            # Validate and clean label
            cleaned_annotations = self._clean_label(label_path)

            if len(cleaned_annotations) == 0:
                self.results['removed_invalid_labels'] += 1
                continue

            # Generate clean filename
            if self.normalize_names:
                new_filename = f"img_{processed_count:06d}{img_path.suffix}"
            else:
                new_filename = img_path.name

            # Copy image to output
            output_img_path = output_images_dir / new_filename
            shutil.copy2(img_path, output_img_path)

            # Write cleaned label
            output_label_path = output_labels_dir / f"{output_img_path.stem}.txt"
            self._write_label(output_label_path, cleaned_annotations)

            processed_count += 1

        self.results['final_count'] = processed_count

        # Generate summary
        summary = self._generate_summary()

        return summary

    def _get_image_files(self, images_dir: Path) -> List[Path]:
        """Get all image files from directory"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        image_files = []

        for ext in image_extensions:
            image_files.extend(images_dir.glob(f'*{ext}'))
            image_files.extend(images_dir.glob(f'*{ext.upper()}'))

        return sorted(image_files)

    def _is_valid_image(self, img_path: Path) -> bool:
        """Check if image is valid and readable"""
        try:
            img = cv2.imread(str(img_path))

            if img is None:
                return False

            height, width = img.shape[:2]

            if height < self.min_image_size[1] or width < self.min_image_size[0]:
                return False

            return True

        except Exception:
            return False

    def _compute_image_hash(self, img_path: Path) -> str:
        """Compute perceptual hash of image for duplicate detection"""
        try:
            # Use perceptual hashing (more robust than MD5)
            img = Image.open(img_path)
            img_hash = str(imagehash.phash(img))
            return img_hash

        except Exception:
            # Fallback to file hash
            return self._compute_file_hash(img_path)

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute file hash (MD5)"""
        hasher = hashlib.md5()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)

        return hasher.hexdigest()

    def _clean_label(self, label_path: Path) -> List[List[float]]:
        """
        Clean and validate label file

        Returns:
            List of valid annotations
        """
        try:
            with open(label_path, 'r') as f:
                lines = f.readlines()

            cleaned_annotations = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()

                if len(parts) != 5:
                    continue

                try:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])

                except ValueError:
                    continue

                # Validate class ID
                if class_id < 0 or class_id >= self.num_classes:
                    continue

                # Validate and fix bbox
                bbox_valid, fixed_bbox = self._validate_and_fix_bbox(
                    x_center, y_center, width, height
                )

                if not bbox_valid:
                    continue

                if fixed_bbox:
                    x_center, y_center, width, height = fixed_bbox
                    self.results['fixed_bboxes'] += 1

                cleaned_annotations.append([class_id, x_center, y_center, width, height])

            return cleaned_annotations

        except Exception:
            return []

    def _validate_and_fix_bbox(
        self,
        x_center: float,
        y_center: float,
        width: float,
        height: float
    ) -> Tuple[bool, Optional[List[float]]]:
        """
        Validate and fix bounding box

        Returns:
            (is_valid, fixed_bbox or None)
        """
        # Check for zero or negative dimensions
        if width <= 0 or height <= 0:
            return False, None

        # Check area threshold
        area = width * height
        if area < 0.0001:
            return False, None

        # Fix coordinates if out of range
        fixed = False
        fixed_bbox = [x_center, y_center, width, height]

        # Clip center coordinates
        if not (0 <= x_center <= 1):
            fixed_bbox[0] = max(0, min(1, x_center))
            fixed = True

        if not (0 <= y_center <= 1):
            fixed_bbox[1] = max(0, min(1, y_center))
            fixed = True

        # Clip dimensions
        if not (0 < width <= 1):
            fixed_bbox[2] = max(0.001, min(1, width))
            fixed = True

        if not (0 < height <= 1):
            fixed_bbox[3] = max(0.001, min(1, height))
            fixed = True

        # Check bbox boundaries
        x1 = fixed_bbox[0] - fixed_bbox[2] / 2
        y1 = fixed_bbox[1] - fixed_bbox[3] / 2
        x2 = fixed_bbox[0] + fixed_bbox[2] / 2
        y2 = fixed_bbox[1] + fixed_bbox[3] / 2

        if x1 < 0 or y1 < 0 or x2 > 1 or y2 > 1:
            # Clip to valid range
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(1, x2)
            y2 = min(1, y2)

            # Recalculate center and dimensions
            fixed_bbox[0] = (x1 + x2) / 2
            fixed_bbox[1] = (y1 + y2) / 2
            fixed_bbox[2] = x2 - x1
            fixed_bbox[3] = y2 - y1
            fixed = True

        # Final area check after fixing
        if fixed_bbox[2] * fixed_bbox[3] < 0.0001:
            return False, None

        return True, (fixed_bbox if fixed else None)

    def _write_label(self, label_path: Path, annotations: List[List[float]]):
        """Write cleaned annotations to label file"""
        with open(label_path, 'w') as f:
            for ann in annotations:
                class_id, x, y, w, h = ann
                f.write(f"{int(class_id)} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

    def _generate_summary(self) -> Dict:
        """Generate cleaning summary"""
        self.logger.subsection("Cleaning Summary")

        summary = {
            'total_processed': self.results['total_processed'],
            'removed_corrupt': self.results['removed_corrupt'],
            'removed_duplicates': self.results['removed_duplicates'],
            'removed_no_labels': self.results['removed_no_labels'],
            'removed_invalid_labels': self.results['removed_invalid_labels'],
            'fixed_bboxes': self.results['fixed_bboxes'],
            'final_count': self.results['final_count'],
            'removal_rate': (
                (self.results['total_processed'] - self.results['final_count']) /
                self.results['total_processed'] * 100
                if self.results['total_processed'] > 0 else 0
            )
        }

        self.logger.info(f"Total Processed: {summary['total_processed']}")
        self.logger.info(f"Removed Corrupt: {summary['removed_corrupt']}")
        self.logger.info(f"Removed Duplicates: {summary['removed_duplicates']}")
        self.logger.info(f"Removed No Labels: {summary['removed_no_labels']}")
        self.logger.info(f"Removed Invalid: {summary['removed_invalid_labels']}")
        self.logger.info(f"Fixed Bboxes: {summary['fixed_bboxes']}")
        self.logger.info(f"Final Count: {summary['final_count']}")
        self.logger.info(f"Removal Rate: {summary['removal_rate']:.2f}%")

        self.logger.success("Dataset cleaning completed")

        return summary
