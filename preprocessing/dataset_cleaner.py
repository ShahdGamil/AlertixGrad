"""
Dataset Cleaning Module for YOLO Format Dataset
Removes corrupted images, invalid bboxes, duplicates, and normalizes file naming.
"""

import os
import shutil
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from PIL import Image
import imagehash
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CleaningResult:
    """Results of dataset cleaning."""
    removed_corrupt_images: List[str] = field(default_factory=list)
    removed_invalid_labels: List[str] = field(default_factory=list)
    removed_duplicates: List[Tuple[str, str]] = field(default_factory=list)
    removed_orphaned_labels: List[str] = field(default_factory=list)
    renamed_files: List[Tuple[str, str]] = field(default_factory=list)
    fixed_labels: List[str] = field(default_factory=list)
    total_images_before: int = 0
    total_images_after: int = 0
    total_labels_before: int = 0
    total_labels_after: int = 0


class DatasetCleaner:
    """Cleans YOLO format dataset for retail theft detection."""

    VALID_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

    def __init__(self, dataset_path: str, num_classes: int = 6,
                 remove_duplicates: bool = True,
                 duplicate_threshold: int = 5,
                 normalize_names: bool = False,
                 backup: bool = True):
        """
        Initialize cleaner.

        Args:
            dataset_path: Root path of the dataset
            num_classes: Number of classes in the dataset
            remove_duplicates: Whether to remove duplicate images
            duplicate_threshold: Hash difference threshold for duplicates (lower = stricter)
            normalize_names: Whether to normalize file naming
            backup: Whether to backup before cleaning
        """
        self.dataset_path = Path(dataset_path)
        self.num_classes = num_classes
        self.remove_duplicates = remove_duplicates
        self.duplicate_threshold = duplicate_threshold
        self.normalize_names = normalize_names
        self.backup = backup
        self.result = CleaningResult()

    def clean_all(self) -> CleaningResult:
        """Run all cleaning operations on the dataset."""
        logger.info("Starting dataset cleaning...")

        if self.backup:
            self._create_backup()

        for split in ['train', 'valid', 'test']:
            split_path = self.dataset_path / split
            if split_path.exists():
                logger.info(f"Cleaning {split} split...")
                self._clean_split(split_path, split)

        self._log_summary()
        return self.result

    def _create_backup(self):
        """Create a backup directory for removed files."""
        backup_path = self.dataset_path / 'backup_removed'
        backup_path.mkdir(exist_ok=True)
        for split in ['train', 'valid', 'test']:
            (backup_path / split / 'images').mkdir(parents=True, exist_ok=True)
            (backup_path / split / 'labels').mkdir(parents=True, exist_ok=True)
        logger.info(f"Backup directory created at: {backup_path}")

    def _clean_split(self, split_path: Path, split_name: str):
        """Clean a single split (train/valid/test)."""
        images_path = split_path / 'images'
        labels_path = split_path / 'labels'

        if not images_path.exists() or not labels_path.exists():
            logger.warning(f"Split {split_name} incomplete, skipping...")
            return

        # Count before
        image_files = list(images_path.glob('*'))
        label_files = list(labels_path.glob('*.txt'))
        self.result.total_images_before += len([f for f in image_files
                                                 if f.suffix.lower() in self.VALID_IMAGE_EXTENSIONS])
        self.result.total_labels_before += len(label_files)

        # Step 1: Remove corrupt images
        self._remove_corrupt_images(images_path, labels_path, split_name)

        # Step 2: Remove invalid labels
        self._remove_invalid_labels(labels_path, split_name)

        # Step 3: Remove orphaned labels
        self._remove_orphaned_labels(images_path, labels_path, split_name)

        # Step 4: Remove duplicates (only for train set typically)
        if self.remove_duplicates and split_name == 'train':
            self._remove_duplicates(images_path, labels_path, split_name)

        # Step 5: Normalize file names (optional)
        if self.normalize_names:
            self._normalize_names(images_path, labels_path)

        # Step 6: Ensure label-image matching
        self._ensure_matching(images_path, labels_path, split_name)

        # Count after
        image_files = list(images_path.glob('*'))
        self.result.total_images_after += len([f for f in image_files
                                                if f.suffix.lower() in self.VALID_IMAGE_EXTENSIONS])
        self.result.total_labels_after += len(list(labels_path.glob('*.txt')))

    def _remove_corrupt_images(self, images_path: Path, labels_path: Path, split_name: str):
        """Remove corrupt or unreadable images and their labels."""
        backup_path = self.dataset_path / 'backup_removed' / split_name

        for img_path in images_path.iterdir():
            if img_path.suffix.lower() not in self.VALID_IMAGE_EXTENSIONS:
                continue

            try:
                with Image.open(img_path) as img:
                    img.verify()
                # Re-open to fully validate
                with Image.open(img_path) as img:
                    img.load()
            except Exception as e:
                logger.warning(f"Removing corrupt image: {img_path.name} - {e}")

                # Move to backup
                if self.backup:
                    shutil.move(str(img_path), str(backup_path / 'images' / img_path.name))
                else:
                    img_path.unlink()

                # Also remove corresponding label
                label_path = labels_path / f"{img_path.stem}.txt"
                if label_path.exists():
                    if self.backup:
                        shutil.move(str(label_path), str(backup_path / 'labels' / label_path.name))
                    else:
                        label_path.unlink()

                self.result.removed_corrupt_images.append(str(img_path))

    def _remove_invalid_labels(self, labels_path: Path, split_name: str):
        """Remove or fix labels with invalid content."""
        backup_path = self.dataset_path / 'backup_removed' / split_name

        for label_path in labels_path.glob('*.txt'):
            try:
                content = label_path.read_text().strip()
                if not content:
                    continue  # Empty labels are valid (background images)

                lines = content.split('\n')
                valid_lines = []
                modified = False

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split()
                    if len(parts) != 5:
                        modified = True
                        continue

                    try:
                        class_id = int(parts[0])
                        values = [float(p) for p in parts[1:]]

                        # Check class ID validity
                        if class_id < 0 or class_id >= self.num_classes:
                            modified = True
                            continue

                        # Check and fix bbox values
                        x_center, y_center, width, height = values

                        # Skip invalid bboxes
                        if width <= 0 or height <= 0:
                            modified = True
                            continue

                        # Clip values to [0, 1]
                        x_center = max(0.0, min(1.0, x_center))
                        y_center = max(0.0, min(1.0, y_center))
                        width = max(0.001, min(1.0, width))
                        height = max(0.001, min(1.0, height))

                        # Ensure bbox doesn't extend beyond image
                        if x_center - width/2 < 0:
                            width = x_center * 2
                        if x_center + width/2 > 1:
                            width = (1 - x_center) * 2
                        if y_center - height/2 < 0:
                            height = y_center * 2
                        if y_center + height/2 > 1:
                            height = (1 - y_center) * 2

                        valid_lines.append(f"{class_id} {x_center:.10f} {y_center:.10f} {width:.10f} {height:.10f}")

                    except ValueError:
                        modified = True
                        continue

                if modified:
                    if valid_lines:
                        label_path.write_text('\n'.join(valid_lines))
                        self.result.fixed_labels.append(str(label_path))
                    else:
                        # No valid lines, remove or backup
                        if self.backup:
                            shutil.move(str(label_path), str(backup_path / 'labels' / label_path.name))
                        else:
                            label_path.unlink()
                        self.result.removed_invalid_labels.append(str(label_path))

            except Exception as e:
                logger.error(f"Error processing label {label_path}: {e}")

    def _remove_orphaned_labels(self, images_path: Path, labels_path: Path, split_name: str):
        """Remove labels without corresponding images."""
        backup_path = self.dataset_path / 'backup_removed' / split_name

        image_stems = {f.stem for f in images_path.iterdir()
                       if f.suffix.lower() in self.VALID_IMAGE_EXTENSIONS}

        for label_path in labels_path.glob('*.txt'):
            if label_path.stem not in image_stems:
                logger.warning(f"Removing orphaned label: {label_path.name}")
                if self.backup:
                    shutil.move(str(label_path), str(backup_path / 'labels' / label_path.name))
                else:
                    label_path.unlink()
                self.result.removed_orphaned_labels.append(str(label_path))

    def _remove_duplicates(self, images_path: Path, labels_path: Path, split_name: str):
        """Remove duplicate images using perceptual hashing."""
        backup_path = self.dataset_path / 'backup_removed' / split_name

        logger.info("Computing image hashes for duplicate detection...")
        hash_to_files: Dict[str, List[Path]] = defaultdict(list)

        for img_path in images_path.iterdir():
            if img_path.suffix.lower() not in self.VALID_IMAGE_EXTENSIONS:
                continue

            try:
                with Image.open(img_path) as img:
                    # Use average hash for speed
                    img_hash = str(imagehash.average_hash(img, hash_size=8))
                    hash_to_files[img_hash].append(img_path)
            except Exception as e:
                logger.warning(f"Could not hash {img_path.name}: {e}")

        # Find and remove duplicates
        for hash_val, files in hash_to_files.items():
            if len(files) > 1:
                # Keep the first file, remove the rest
                original = files[0]
                for duplicate in files[1:]:
                    logger.info(f"Removing duplicate: {duplicate.name} (duplicate of {original.name})")

                    # Move to backup
                    if self.backup:
                        shutil.move(str(duplicate), str(backup_path / 'images' / duplicate.name))
                    else:
                        duplicate.unlink()

                    # Also remove corresponding label
                    label_path = labels_path / f"{duplicate.stem}.txt"
                    if label_path.exists():
                        if self.backup:
                            shutil.move(str(label_path), str(backup_path / 'labels' / label_path.name))
                        else:
                            label_path.unlink()

                    self.result.removed_duplicates.append((str(duplicate), str(original)))

    def _normalize_names(self, images_path: Path, labels_path: Path):
        """Normalize file naming conventions."""
        counter = 0

        for img_path in sorted(images_path.iterdir()):
            if img_path.suffix.lower() not in self.VALID_IMAGE_EXTENSIONS:
                continue

            # Create normalized name
            new_name = f"img_{counter:06d}{img_path.suffix.lower()}"
            new_img_path = images_path / new_name

            # Skip if already normalized
            if img_path.name == new_name:
                counter += 1
                continue

            # Rename image
            old_path = str(img_path)
            img_path.rename(new_img_path)

            # Rename corresponding label
            old_label_path = labels_path / f"{img_path.stem}.txt"
            new_label_path = labels_path / f"img_{counter:06d}.txt"

            if old_label_path.exists():
                old_label_path.rename(new_label_path)

            self.result.renamed_files.append((old_path, str(new_img_path)))
            counter += 1

    def _ensure_matching(self, images_path: Path, labels_path: Path, split_name: str):
        """Ensure all images have corresponding labels (create empty if missing)."""
        label_stems = {f.stem for f in labels_path.glob('*.txt')}

        for img_path in images_path.iterdir():
            if img_path.suffix.lower() not in self.VALID_IMAGE_EXTENSIONS:
                continue

            if img_path.stem not in label_stems:
                # Create empty label file
                label_path = labels_path / f"{img_path.stem}.txt"
                label_path.touch()
                logger.info(f"Created empty label for: {img_path.name}")

    def _log_summary(self):
        """Log cleaning summary."""
        logger.info("=" * 60)
        logger.info("DATASET CLEANING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Images before: {self.result.total_images_before}")
        logger.info(f"Images after: {self.result.total_images_after}")
        logger.info(f"Labels before: {self.result.total_labels_before}")
        logger.info(f"Labels after: {self.result.total_labels_after}")
        logger.info("-" * 60)
        logger.info(f"Removed corrupt images: {len(self.result.removed_corrupt_images)}")
        logger.info(f"Removed invalid labels: {len(self.result.removed_invalid_labels)}")
        logger.info(f"Removed duplicates: {len(self.result.removed_duplicates)}")
        logger.info(f"Removed orphaned labels: {len(self.result.removed_orphaned_labels)}")
        logger.info(f"Fixed labels: {len(self.result.fixed_labels)}")
        if self.normalize_names:
            logger.info(f"Renamed files: {len(self.result.renamed_files)}")
        logger.info("=" * 60)


def clean_dataset(dataset_path: str, num_classes: int = 6, **kwargs) -> CleaningResult:
    """
    Convenience function to clean a dataset.

    Args:
        dataset_path: Path to the dataset root
        num_classes: Number of classes
        **kwargs: Additional arguments for DatasetCleaner

    Returns:
        CleaningResult with all actions taken
    """
    cleaner = DatasetCleaner(dataset_path, num_classes, **kwargs)
    return cleaner.clean_all()


if __name__ == "__main__":
    import sys
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "."
    result = clean_dataset(dataset_path)
