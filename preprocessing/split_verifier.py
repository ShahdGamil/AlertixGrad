"""
Dataset Split Verification Module for YOLO Format Dataset
Ensures train/val/test splits are mutually exclusive with no duplicates.
Provides comprehensive reporting and visualization.
"""

import os
import csv
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
import json
import shutil

try:
    from PIL import Image
    import imagehash
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('split_check.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class SplitVerificationResult:
    """Results of split verification."""
    # Per-split statistics
    images_per_split: Dict[str, int] = field(default_factory=dict)
    labels_per_split: Dict[str, int] = field(default_factory=dict)

    # Duplicates within splits
    duplicates_within_splits: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)

    # Overlaps between splits
    filename_overlaps: List[Dict[str, any]] = field(default_factory=list)
    content_overlaps: List[Dict[str, any]] = field(default_factory=list)

    # Missing labels
    missing_labels: Dict[str, List[str]] = field(default_factory=dict)
    orphaned_labels: Dict[str, List[str]] = field(default_factory=dict)

    # Invalid bounding boxes
    invalid_bboxes: Dict[str, List[Dict]] = field(default_factory=dict)

    # Summary
    total_unique_images: int = 0
    total_overlaps: int = 0
    total_errors: int = 0
    is_valid: bool = True

    # Actions taken (for auto-fix)
    actions_taken: List[str] = field(default_factory=list)


class DatasetSplitVerifier:
    """
    Verifies YOLO dataset splits are mutually exclusive and valid.
    """

    VALID_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    CLASS_NAMES = ['Customer-Bagpack', 'Product', 'Product-Picked',
                   'Shopping-Cart', 'normal', 'theft']

    def __init__(self, dataset_path: str,
                 splits: List[str] = None,
                 check_content_duplicates: bool = True):
        """
        Initialize verifier.

        Args:
            dataset_path: Root path of the dataset
            splits: List of split names (default: ['train', 'valid', 'test'])
            check_content_duplicates: Whether to check for content-based duplicates
        """
        self.dataset_path = Path(dataset_path)
        self.splits = splits or ['train', 'valid', 'test']
        self.check_content_duplicates = check_content_duplicates
        self.result = SplitVerificationResult()
        self.reports_path = self.dataset_path / 'reports'
        self.reports_path.mkdir(exist_ok=True)

    def verify_all(self) -> SplitVerificationResult:
        """Run all verification checks."""
        logger.info("=" * 70)
        logger.info("DATASET SPLIT VERIFICATION")
        logger.info("=" * 70)

        # Collect all files per split
        split_files = self._collect_files()

        # Check 1: Duplicates within each split
        logger.info("\n[CHECK 1] Detecting duplicates within splits...")
        self._check_duplicates_within_splits(split_files)

        # Check 2: Overlapping filenames across splits
        logger.info("\n[CHECK 2] Detecting filename overlaps across splits...")
        self._check_filename_overlaps(split_files)

        # Check 3: Content-based duplicates across splits
        if self.check_content_duplicates and HAS_PIL:
            logger.info("\n[CHECK 3] Detecting content-based overlaps across splits...")
            self._check_content_overlaps(split_files)

        # Check 4: Missing labels
        logger.info("\n[CHECK 4] Detecting missing labels...")
        self._check_missing_labels(split_files)

        # Check 5: Validate bounding boxes
        logger.info("\n[CHECK 5] Validating bounding boxes...")
        self._validate_bboxes(split_files)

        # Calculate summary statistics
        self._calculate_summary(split_files)

        # Generate reports
        self._generate_reports()

        return self.result

    def _collect_files(self) -> Dict[str, Dict[str, Set[str]]]:
        """Collect all image and label files per split."""
        split_files = {}

        for split in self.splits:
            split_path = self.dataset_path / split
            images_path = split_path / 'images'
            labels_path = split_path / 'labels'

            split_files[split] = {
                'images': set(),
                'labels': set(),
                'image_paths': {},
                'label_paths': {}
            }

            if images_path.exists():
                for img_file in images_path.iterdir():
                    if img_file.suffix.lower() in self.VALID_IMAGE_EXTENSIONS:
                        split_files[split]['images'].add(img_file.stem)
                        split_files[split]['image_paths'][img_file.stem] = img_file

            if labels_path.exists():
                for lbl_file in labels_path.glob('*.txt'):
                    split_files[split]['labels'].add(lbl_file.stem)
                    split_files[split]['label_paths'][lbl_file.stem] = lbl_file

            self.result.images_per_split[split] = len(split_files[split]['images'])
            self.result.labels_per_split[split] = len(split_files[split]['labels'])

            logger.info(f"  {split}: {len(split_files[split]['images'])} images, "
                       f"{len(split_files[split]['labels'])} labels")

        return split_files

    def _check_duplicates_within_splits(self, split_files: Dict):
        """Check for duplicate filenames within each split."""
        for split in self.splits:
            self.result.duplicates_within_splits[split] = []

            # Get image paths
            images_path = self.dataset_path / split / 'images'
            if not images_path.exists():
                continue

            # Check for content-based duplicates using hashing
            if HAS_PIL:
                hash_to_files = defaultdict(list)

                for img_file in images_path.iterdir():
                    if img_file.suffix.lower() not in self.VALID_IMAGE_EXTENSIONS:
                        continue

                    try:
                        with Image.open(img_file) as img:
                            img_hash = str(imagehash.average_hash(img, hash_size=8))
                            hash_to_files[img_hash].append(img_file.name)
                    except Exception as e:
                        logger.warning(f"Could not hash {img_file.name}: {e}")

                for hash_val, files in hash_to_files.items():
                    if len(files) > 1:
                        for i, f1 in enumerate(files):
                            for f2 in files[i+1:]:
                                self.result.duplicates_within_splits[split].append((f1, f2))

            dup_count = len(self.result.duplicates_within_splits[split])
            if dup_count > 0:
                logger.warning(f"  {split}: Found {dup_count} duplicate pairs")
                self.result.is_valid = False
            else:
                logger.info(f"  {split}: No duplicates found")

    def _check_filename_overlaps(self, split_files: Dict):
        """Check for overlapping filenames across splits."""
        splits = list(split_files.keys())

        for i, split1 in enumerate(splits):
            for split2 in splits[i+1:]:
                overlap = split_files[split1]['images'] & split_files[split2]['images']

                for filename in overlap:
                    self.result.filename_overlaps.append({
                        'filename': filename,
                        'splits': [split1, split2],
                        'type': 'filename_match'
                    })

        if self.result.filename_overlaps:
            logger.warning(f"  Found {len(self.result.filename_overlaps)} filename overlaps!")
            self.result.is_valid = False
            for overlap in self.result.filename_overlaps[:5]:
                logger.warning(f"    {overlap['filename']}: {overlap['splits']}")
            if len(self.result.filename_overlaps) > 5:
                logger.warning(f"    ... and {len(self.result.filename_overlaps) - 5} more")
        else:
            logger.info("  No filename overlaps found across splits")

    def _check_content_overlaps(self, split_files: Dict):
        """Check for content-based duplicates across splits using perceptual hashing."""
        logger.info("  Computing image hashes...")

        # Collect hashes for all images
        all_hashes = {}  # hash -> [(split, filename, path), ...]

        for split in self.splits:
            for stem, img_path in split_files[split].get('image_paths', {}).items():
                try:
                    with Image.open(img_path) as img:
                        img_hash = str(imagehash.average_hash(img, hash_size=8))

                        if img_hash not in all_hashes:
                            all_hashes[img_hash] = []
                        all_hashes[img_hash].append((split, stem, img_path))
                except Exception as e:
                    logger.warning(f"Could not hash {img_path.name}: {e}")

        # Find cross-split duplicates
        for img_hash, files in all_hashes.items():
            if len(files) > 1:
                # Check if files are from different splits
                splits_with_hash = set(f[0] for f in files)
                if len(splits_with_hash) > 1:
                    self.result.content_overlaps.append({
                        'hash': img_hash,
                        'files': [(f[0], f[1]) for f in files],
                        'type': 'content_match'
                    })

        if self.result.content_overlaps:
            logger.warning(f"  Found {len(self.result.content_overlaps)} content-based overlaps!")
            self.result.is_valid = False
            for overlap in self.result.content_overlaps[:5]:
                logger.warning(f"    Hash {overlap['hash'][:8]}...: {overlap['files']}")
        else:
            logger.info("  No content-based overlaps found across splits")

    def _check_missing_labels(self, split_files: Dict):
        """Check for images without labels and orphaned labels."""
        for split in self.splits:
            images = split_files[split]['images']
            labels = split_files[split]['labels']

            # Images without labels
            missing = images - labels
            self.result.missing_labels[split] = list(missing)

            # Labels without images (orphaned)
            orphaned = labels - images
            self.result.orphaned_labels[split] = list(orphaned)

            if missing:
                logger.warning(f"  {split}: {len(missing)} images missing labels")
            if orphaned:
                logger.warning(f"  {split}: {len(orphaned)} orphaned labels")
            if not missing and not orphaned:
                logger.info(f"  {split}: All images have matching labels")

    def _validate_bboxes(self, split_files: Dict):
        """Validate bounding box coordinates."""
        for split in self.splits:
            self.result.invalid_bboxes[split] = []
            labels_path = self.dataset_path / split / 'labels'

            if not labels_path.exists():
                continue

            for label_file in labels_path.glob('*.txt'):
                content = label_file.read_text().strip()
                if not content:
                    continue

                for line_num, line in enumerate(content.split('\n'), 1):
                    parts = line.strip().split()
                    if len(parts) != 5:
                        self.result.invalid_bboxes[split].append({
                            'file': label_file.name,
                            'line': line_num,
                            'error': f'Invalid format: expected 5 values, got {len(parts)}'
                        })
                        continue

                    try:
                        class_id = int(parts[0])
                        x_center, y_center, width, height = map(float, parts[1:])

                        errors = []
                        if class_id < 0 or class_id >= len(self.CLASS_NAMES):
                            errors.append(f'Invalid class_id: {class_id}')
                        if not (0 <= x_center <= 1):
                            errors.append(f'x_center out of range: {x_center}')
                        if not (0 <= y_center <= 1):
                            errors.append(f'y_center out of range: {y_center}')
                        if not (0 < width <= 1):
                            errors.append(f'width out of range: {width}')
                        if not (0 < height <= 1):
                            errors.append(f'height out of range: {height}')

                        # Check if bbox extends beyond image
                        if x_center - width/2 < 0 or x_center + width/2 > 1:
                            errors.append('bbox extends beyond image (x)')
                        if y_center - height/2 < 0 or y_center + height/2 > 1:
                            errors.append('bbox extends beyond image (y)')

                        if errors:
                            self.result.invalid_bboxes[split].append({
                                'file': label_file.name,
                                'line': line_num,
                                'error': '; '.join(errors)
                            })

                    except ValueError as e:
                        self.result.invalid_bboxes[split].append({
                            'file': label_file.name,
                            'line': line_num,
                            'error': f'Parse error: {e}'
                        })

            invalid_count = len(self.result.invalid_bboxes[split])
            if invalid_count > 0:
                logger.warning(f"  {split}: {invalid_count} invalid bounding boxes")
            else:
                logger.info(f"  {split}: All bounding boxes valid")

    def _calculate_summary(self, split_files: Dict):
        """Calculate summary statistics."""
        # Total unique images
        all_images = set()
        for split in self.splits:
            all_images.update(split_files[split]['images'])
        self.result.total_unique_images = len(all_images)

        # Total overlaps
        self.result.total_overlaps = (
            len(self.result.filename_overlaps) +
            len(self.result.content_overlaps)
        )

        # Total errors
        total_missing = sum(len(v) for v in self.result.missing_labels.values())
        total_orphaned = sum(len(v) for v in self.result.orphaned_labels.values())
        total_invalid_bbox = sum(len(v) for v in self.result.invalid_bboxes.values())
        total_duplicates = sum(len(v) for v in self.result.duplicates_within_splits.values())

        self.result.total_errors = (
            total_missing + total_orphaned +
            total_invalid_bbox + total_duplicates +
            self.result.total_overlaps
        )

        if self.result.total_errors > 0:
            self.result.is_valid = False

    def auto_fix(self,
                 remove_duplicates: bool = True,
                 move_overlaps_to_train: bool = True,
                 create_missing_labels: bool = True,
                 remove_orphaned_labels: bool = True) -> List[str]:
        """
        Automatically fix detected issues.

        Args:
            remove_duplicates: Remove duplicate images within splits
            move_overlaps_to_train: Move overlapping images to train split
            create_missing_labels: Create empty labels for images without labels
            remove_orphaned_labels: Remove labels without corresponding images

        Returns:
            List of actions taken
        """
        actions = []
        backup_path = self.dataset_path / 'backup_split_fix'
        backup_path.mkdir(exist_ok=True)

        # Fix duplicates within splits
        if remove_duplicates:
            for split, duplicates in self.result.duplicates_within_splits.items():
                for dup1, dup2 in duplicates:
                    dup_path = self.dataset_path / split / 'images' / dup2
                    if dup_path.exists():
                        backup_dest = backup_path / split / 'images'
                        backup_dest.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(dup_path), str(backup_dest / dup2))
                        action = f"Removed duplicate {split}/images/{dup2} (duplicate of {dup1})"
                        actions.append(action)
                        logger.info(action)

                        # Also remove corresponding label
                        dup_label = self.dataset_path / split / 'labels' / f"{Path(dup2).stem}.txt"
                        if dup_label.exists():
                            backup_lbl = backup_path / split / 'labels'
                            backup_lbl.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(dup_label), str(backup_lbl / dup_label.name))

        # Fix overlaps between splits
        if move_overlaps_to_train:
            for overlap in self.result.filename_overlaps:
                filename = overlap['filename']
                for split in overlap['splits']:
                    if split != 'train':
                        # Move to backup instead of train
                        for ext in ['.jpg', '.jpeg', '.png']:
                            img_path = self.dataset_path / split / 'images' / f"{filename}{ext}"
                            if img_path.exists():
                                backup_dest = backup_path / split / 'images'
                                backup_dest.mkdir(parents=True, exist_ok=True)
                                shutil.move(str(img_path), str(backup_dest / img_path.name))
                                action = f"Removed overlapping {split}/images/{img_path.name}"
                                actions.append(action)
                                logger.info(action)

                                # Also handle label
                                lbl_path = self.dataset_path / split / 'labels' / f"{filename}.txt"
                                if lbl_path.exists():
                                    backup_lbl = backup_path / split / 'labels'
                                    backup_lbl.mkdir(parents=True, exist_ok=True)
                                    shutil.move(str(lbl_path), str(backup_lbl / lbl_path.name))
                                break

        # Create missing labels
        if create_missing_labels:
            for split, missing in self.result.missing_labels.items():
                labels_path = self.dataset_path / split / 'labels'
                for filename in missing:
                    label_file = labels_path / f"{filename}.txt"
                    label_file.touch()
                    action = f"Created empty label: {split}/labels/{filename}.txt"
                    actions.append(action)
                    logger.info(action)

        # Remove orphaned labels
        if remove_orphaned_labels:
            for split, orphaned in self.result.orphaned_labels.items():
                labels_path = self.dataset_path / split / 'labels'
                for filename in orphaned:
                    label_file = labels_path / f"{filename}.txt"
                    if label_file.exists():
                        backup_dest = backup_path / split / 'labels'
                        backup_dest.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(label_file), str(backup_dest / label_file.name))
                        action = f"Removed orphaned label: {split}/labels/{filename}.txt"
                        actions.append(action)
                        logger.info(action)

        self.result.actions_taken = actions
        logger.info(f"\nTotal actions taken: {len(actions)}")
        return actions

    def _generate_reports(self):
        """Generate verification reports."""
        # CSV Report
        self._generate_csv_report()

        # JSON Report
        self._generate_json_report()

        # Text Summary
        self._generate_text_summary()

    def _generate_csv_report(self):
        """Generate CSV report of issues."""
        csv_file = self.reports_path / 'split_verification_issues.csv'

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Issue Type', 'Split', 'File/Details', 'Additional Info'])

            # Duplicates within splits
            for split, dups in self.result.duplicates_within_splits.items():
                for dup1, dup2 in dups:
                    writer.writerow(['Duplicate Within Split', split, dup1, f'Duplicate of: {dup2}'])

            # Filename overlaps
            for overlap in self.result.filename_overlaps:
                writer.writerow(['Filename Overlap', ','.join(overlap['splits']),
                               overlap['filename'], 'Same filename in multiple splits'])

            # Content overlaps
            for overlap in self.result.content_overlaps:
                files_str = '; '.join([f"{s}:{f}" for s, f in overlap['files']])
                writer.writerow(['Content Overlap', 'Multiple', files_str,
                               f"Hash: {overlap['hash'][:16]}"])

            # Missing labels
            for split, missing in self.result.missing_labels.items():
                for filename in missing:
                    writer.writerow(['Missing Label', split, filename, 'Image without label'])

            # Orphaned labels
            for split, orphaned in self.result.orphaned_labels.items():
                for filename in orphaned:
                    writer.writerow(['Orphaned Label', split, filename, 'Label without image'])

            # Invalid bboxes
            for split, invalids in self.result.invalid_bboxes.items():
                for invalid in invalids:
                    writer.writerow(['Invalid BBox', split, invalid['file'],
                                   f"Line {invalid['line']}: {invalid['error']}"])

        logger.info(f"CSV report saved to: {csv_file}")

    def _generate_json_report(self):
        """Generate JSON report."""
        json_file = self.reports_path / 'split_verification_report.json'

        report = {
            'generated_at': datetime.now().isoformat(),
            'dataset_path': str(self.dataset_path),
            'is_valid': self.result.is_valid,
            'summary': {
                'images_per_split': self.result.images_per_split,
                'labels_per_split': self.result.labels_per_split,
                'total_unique_images': self.result.total_unique_images,
                'total_overlaps': self.result.total_overlaps,
                'total_errors': self.result.total_errors
            },
            'duplicates_within_splits': {
                split: len(dups) for split, dups in self.result.duplicates_within_splits.items()
            },
            'filename_overlaps': len(self.result.filename_overlaps),
            'content_overlaps': len(self.result.content_overlaps),
            'missing_labels': {
                split: len(missing) for split, missing in self.result.missing_labels.items()
            },
            'orphaned_labels': {
                split: len(orphaned) for split, orphaned in self.result.orphaned_labels.items()
            },
            'invalid_bboxes': {
                split: len(invalids) for split, invalids in self.result.invalid_bboxes.items()
            },
            'details': {
                'filename_overlaps': self.result.filename_overlaps[:20],
                'content_overlaps': self.result.content_overlaps[:20]
            }
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"JSON report saved to: {json_file}")

    def _generate_text_summary(self):
        """Generate text summary report."""
        txt_file = self.reports_path / 'split_verification_summary.txt'

        lines = [
            "=" * 70,
            "DATASET SPLIT VERIFICATION SUMMARY",
            "=" * 70,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Dataset: {self.dataset_path}",
            "",
            "SPLIT STATISTICS:",
            "-" * 40
        ]

        for split in self.splits:
            lines.append(f"  {split}:")
            lines.append(f"    Images: {self.result.images_per_split.get(split, 0)}")
            lines.append(f"    Labels: {self.result.labels_per_split.get(split, 0)}")

        lines.extend([
            "",
            f"Total Unique Images: {self.result.total_unique_images}",
            "",
            "ISSUES DETECTED:",
            "-" * 40
        ])

        # Duplicates
        total_dups = sum(len(v) for v in self.result.duplicates_within_splits.values())
        lines.append(f"  Duplicates within splits: {total_dups}")

        # Overlaps
        lines.append(f"  Filename overlaps: {len(self.result.filename_overlaps)}")
        lines.append(f"  Content overlaps: {len(self.result.content_overlaps)}")

        # Missing/Orphaned
        total_missing = sum(len(v) for v in self.result.missing_labels.values())
        total_orphaned = sum(len(v) for v in self.result.orphaned_labels.values())
        lines.append(f"  Missing labels: {total_missing}")
        lines.append(f"  Orphaned labels: {total_orphaned}")

        # Invalid bboxes
        total_invalid = sum(len(v) for v in self.result.invalid_bboxes.values())
        lines.append(f"  Invalid bounding boxes: {total_invalid}")

        lines.extend([
            "",
            "-" * 40,
            f"TOTAL ERRORS: {self.result.total_errors}",
            f"VALIDATION STATUS: {'PASSED' if self.result.is_valid else 'FAILED'}",
            "=" * 70
        ])

        content = '\n'.join(lines)
        txt_file.write_text(content, encoding='utf-8')
        logger.info(f"Text summary saved to: {txt_file}")

        # Also print to console
        print(content)


class EnhancedDatasetVisualizer:
    """
    Enhanced visualization for dataset analysis and split verification.
    """

    CLASS_NAMES = ['Customer-Bagpack', 'Product', 'Product-Picked',
                   'Shopping-Cart', 'normal', 'theft']
    CLASS_COLORS = [
        '#FF0000', '#00FF00', '#0000FF',
        '#FFFF00', '#FF00FF', '#FFA500'
    ]

    def __init__(self, dataset_path: str, output_path: str = None):
        self.dataset_path = Path(dataset_path)
        self.output_path = Path(output_path) if output_path else self.dataset_path / 'reports'
        self.output_path.mkdir(exist_ok=True)

    def generate_split_comparison_chart(self):
        """Generate side-by-side split comparison chart."""
        if not HAS_MATPLOTLIB:
            logger.warning("matplotlib not available")
            return None

        splits = ['train', 'valid', 'test']
        class_counts = {split: defaultdict(int) for split in splits}

        # Count classes per split
        for split in splits:
            labels_path = self.dataset_path / split / 'labels'
            if not labels_path.exists():
                continue

            for label_file in labels_path.glob('*.txt'):
                content = label_file.read_text().strip()
                if not content:
                    continue
                for line in content.split('\n'):
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        try:
                            class_id = int(parts[0])
                            class_counts[split][class_id] += 1
                        except:
                            pass

        # Create figure with subplots
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Class Distribution Comparison Across Splits', fontsize=14, fontweight='bold')

        for idx, split in enumerate(splits):
            ax = axes[idx]
            counts = class_counts[split]

            classes = list(range(len(self.CLASS_NAMES)))
            values = [counts.get(c, 0) for c in classes]
            colors = self.CLASS_COLORS[:len(classes)]

            bars = ax.bar(self.CLASS_NAMES, values, color=colors, edgecolor='black')
            ax.set_title(f'{split.capitalize()} Split', fontsize=12, fontweight='bold')
            ax.set_xlabel('Class')
            ax.set_ylabel('Count')
            ax.tick_params(axis='x', rotation=45)

            # Add value labels
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                       str(val), ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        output_file = self.output_path / 'split_comparison_chart.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Split comparison chart saved to: {output_file}")
        return str(output_file)

    def generate_split_pie_charts(self):
        """Generate pie charts showing split proportions."""
        if not HAS_MATPLOTLIB:
            return None

        splits = ['train', 'valid', 'test']
        image_counts = {}
        annotation_counts = {}

        for split in splits:
            images_path = self.dataset_path / split / 'images'
            labels_path = self.dataset_path / split / 'labels'

            image_counts[split] = len(list(images_path.glob('*.jpg'))) if images_path.exists() else 0

            ann_count = 0
            if labels_path.exists():
                for lbl in labels_path.glob('*.txt'):
                    content = lbl.read_text().strip()
                    if content:
                        ann_count += len(content.split('\n'))
            annotation_counts[split] = ann_count

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        colors = ['#2ecc71', '#3498db', '#e74c3c']

        # Images pie chart
        axes[0].pie(
            [image_counts[s] for s in splits],
            labels=[f"{s}\n({image_counts[s]})" for s in splits],
            autopct='%1.1f%%',
            colors=colors,
            explode=[0.02, 0.02, 0.02],
            shadow=True
        )
        axes[0].set_title('Image Distribution Across Splits', fontsize=12, fontweight='bold')

        # Annotations pie chart
        axes[1].pie(
            [annotation_counts[s] for s in splits],
            labels=[f"{s}\n({annotation_counts[s]})" for s in splits],
            autopct='%1.1f%%',
            colors=colors,
            explode=[0.02, 0.02, 0.02],
            shadow=True
        )
        axes[1].set_title('Annotation Distribution Across Splits', fontsize=12, fontweight='bold')

        plt.tight_layout()
        output_file = self.output_path / 'split_pie_charts.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Split pie charts saved to: {output_file}")
        return str(output_file)

    def generate_class_balance_heatmap(self):
        """Generate heatmap showing class balance across splits."""
        if not HAS_MATPLOTLIB or not HAS_NUMPY:
            return None

        splits = ['train', 'valid', 'test']
        class_counts = {split: {} for split in splits}

        for split in splits:
            labels_path = self.dataset_path / split / 'labels'
            if not labels_path.exists():
                continue

            for class_id in range(len(self.CLASS_NAMES)):
                class_counts[split][class_id] = 0

            for label_file in labels_path.glob('*.txt'):
                content = label_file.read_text().strip()
                if not content:
                    continue
                for line in content.split('\n'):
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        try:
                            class_id = int(parts[0])
                            if class_id in class_counts[split]:
                                class_counts[split][class_id] += 1
                        except:
                            pass

        # Create matrix
        matrix = np.zeros((len(self.CLASS_NAMES), len(splits)))
        for col, split in enumerate(splits):
            for row, class_id in enumerate(range(len(self.CLASS_NAMES))):
                matrix[row, col] = class_counts[split].get(class_id, 0)

        # Normalize by row (class) for percentage
        row_sums = matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        matrix_pct = (matrix / row_sums) * 100

        fig, ax = plt.subplots(figsize=(10, 8))

        # Create heatmap
        im = ax.imshow(matrix_pct, cmap='YlOrRd', aspect='auto')

        # Set ticks
        ax.set_xticks(range(len(splits)))
        ax.set_xticklabels([s.capitalize() for s in splits])
        ax.set_yticks(range(len(self.CLASS_NAMES)))
        ax.set_yticklabels(self.CLASS_NAMES)

        # Add text annotations
        for i in range(len(self.CLASS_NAMES)):
            for j in range(len(splits)):
                count = int(matrix[i, j])
                pct = matrix_pct[i, j]
                text = f"{count}\n({pct:.1f}%)"
                ax.text(j, i, text, ha='center', va='center',
                       color='white' if pct > 50 else 'black', fontsize=9)

        ax.set_title('Class Distribution Heatmap (Count & Percentage per Class)',
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('Split')
        ax.set_ylabel('Class')

        plt.colorbar(im, label='Percentage')
        plt.tight_layout()

        output_file = self.output_path / 'class_balance_heatmap.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Class balance heatmap saved to: {output_file}")
        return str(output_file)

    def generate_bbox_analysis_chart(self):
        """Generate comprehensive bounding box analysis."""
        if not HAS_MATPLOTLIB or not HAS_NUMPY:
            return None

        splits = ['train', 'valid', 'test']
        all_widths = {s: [] for s in splits}
        all_heights = {s: [] for s in splits}
        all_areas = {s: [] for s in splits}
        all_aspects = {s: [] for s in splits}

        for split in splits:
            labels_path = self.dataset_path / split / 'labels'
            if not labels_path.exists():
                continue

            for label_file in labels_path.glob('*.txt'):
                content = label_file.read_text().strip()
                if not content:
                    continue
                for line in content.split('\n'):
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        try:
                            width = float(parts[3])
                            height = float(parts[4])
                            all_widths[split].append(width)
                            all_heights[split].append(height)
                            all_areas[split].append(width * height)
                            if height > 0:
                                all_aspects[split].append(width / height)
                        except:
                            pass

        fig, axes = plt.subplots(2, 2, figsize=(14, 12))

        colors = {'train': '#2ecc71', 'valid': '#3498db', 'test': '#e74c3c'}

        # Width distribution
        for split in splits:
            if all_widths[split]:
                axes[0, 0].hist(all_widths[split], bins=50, alpha=0.5,
                               label=split, color=colors[split])
        axes[0, 0].set_title('Bounding Box Width Distribution')
        axes[0, 0].set_xlabel('Normalized Width')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].legend()

        # Height distribution
        for split in splits:
            if all_heights[split]:
                axes[0, 1].hist(all_heights[split], bins=50, alpha=0.5,
                               label=split, color=colors[split])
        axes[0, 1].set_title('Bounding Box Height Distribution')
        axes[0, 1].set_xlabel('Normalized Height')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].legend()

        # Area distribution
        for split in splits:
            if all_areas[split]:
                axes[1, 0].hist(all_areas[split], bins=50, alpha=0.5,
                               label=split, color=colors[split])
        axes[1, 0].set_title('Bounding Box Area Distribution')
        axes[1, 0].set_xlabel('Normalized Area')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].legend()

        # Aspect ratio distribution
        for split in splits:
            if all_aspects[split]:
                axes[1, 1].hist(all_aspects[split], bins=50, alpha=0.5,
                               label=split, color=colors[split], range=(0, 3))
        axes[1, 1].set_title('Bounding Box Aspect Ratio Distribution')
        axes[1, 1].set_xlabel('Aspect Ratio (Width/Height)')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].axvline(x=1.0, color='red', linestyle='--', label='Square (1:1)')
        axes[1, 1].legend()

        plt.tight_layout()
        output_file = self.output_path / 'bbox_analysis_detailed.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"BBox analysis chart saved to: {output_file}")
        return str(output_file)

    def generate_sample_comparison_grid(self, samples_per_split: int = 3):
        """Generate a grid showing sample images from each split side by side."""
        if not HAS_PIL or not HAS_MATPLOTLIB:
            return None

        import random
        random.seed(42)

        splits = ['train', 'valid', 'test']
        fig, axes = plt.subplots(samples_per_split, 3, figsize=(15, 5*samples_per_split))

        for col, split in enumerate(splits):
            images_path = self.dataset_path / split / 'images'
            labels_path = self.dataset_path / split / 'labels'

            if not images_path.exists():
                continue

            image_files = list(images_path.glob('*.jpg'))
            if len(image_files) > samples_per_split:
                image_files = random.sample(image_files, samples_per_split)

            for row, img_path in enumerate(image_files[:samples_per_split]):
                ax = axes[row, col] if samples_per_split > 1 else axes[col]

                try:
                    img = Image.open(img_path)
                    ax.imshow(img)

                    # Draw bounding boxes
                    label_path = labels_path / f"{img_path.stem}.txt"
                    if label_path.exists():
                        content = label_path.read_text().strip()
                        if content:
                            img_w, img_h = img.size
                            for line in content.split('\n'):
                                parts = line.strip().split()
                                if len(parts) >= 5:
                                    try:
                                        class_id = int(parts[0])
                                        x_c, y_c, w, h = map(float, parts[1:5])

                                        # Convert to pixel coordinates
                                        x1 = (x_c - w/2) * img_w
                                        y1 = (y_c - h/2) * img_h
                                        box_w = w * img_w
                                        box_h = h * img_h

                                        color = self.CLASS_COLORS[class_id] if class_id < len(self.CLASS_COLORS) else '#FFFFFF'
                                        rect = Rectangle((x1, y1), box_w, box_h,
                                                        linewidth=2, edgecolor=color,
                                                        facecolor='none')
                                        ax.add_patch(rect)

                                        # Add label
                                        label = self.CLASS_NAMES[class_id] if class_id < len(self.CLASS_NAMES) else f"C{class_id}"
                                        ax.text(x1, y1-5, label[:8], color=color, fontsize=8,
                                               bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
                                    except:
                                        pass

                    ax.axis('off')
                    if row == 0:
                        ax.set_title(f'{split.capitalize()}', fontsize=12, fontweight='bold')

                except Exception as e:
                    ax.text(0.5, 0.5, f'Error: {e}', ha='center', va='center')
                    ax.axis('off')

        plt.suptitle('Sample Images Comparison Across Splits', fontsize=14, fontweight='bold')
        plt.tight_layout()

        output_file = self.output_path / 'sample_comparison_grid.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Sample comparison grid saved to: {output_file}")
        return str(output_file)

    def generate_annotations_per_image_chart(self):
        """Generate chart showing distribution of annotations per image."""
        if not HAS_MATPLOTLIB or not HAS_NUMPY:
            return None

        splits = ['train', 'valid', 'test']
        ann_per_image = {s: [] for s in splits}

        for split in splits:
            labels_path = self.dataset_path / split / 'labels'
            if not labels_path.exists():
                continue

            for label_file in labels_path.glob('*.txt'):
                content = label_file.read_text().strip()
                count = len(content.split('\n')) if content else 0
                ann_per_image[split].append(count)

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        colors = {'train': '#2ecc71', 'valid': '#3498db', 'test': '#e74c3c'}

        # Histogram
        for split in splits:
            if ann_per_image[split]:
                axes[0].hist(ann_per_image[split], bins=range(0, max(max(ann_per_image[split]), 10)+2),
                           alpha=0.5, label=f"{split} (avg: {np.mean(ann_per_image[split]):.1f})",
                           color=colors[split])
        axes[0].set_title('Distribution of Annotations per Image')
        axes[0].set_xlabel('Number of Annotations')
        axes[0].set_ylabel('Number of Images')
        axes[0].legend()

        # Box plot
        data = [ann_per_image[s] for s in splits if ann_per_image[s]]
        labels = [s for s in splits if ann_per_image[s]]
        bp = axes[1].boxplot(data, labels=labels, patch_artist=True)
        for patch, color in zip(bp['boxes'], [colors[s] for s in labels]):
            patch.set_facecolor(color)
            patch.set_alpha(0.5)
        axes[1].set_title('Annotations per Image by Split')
        axes[1].set_ylabel('Number of Annotations')

        plt.tight_layout()
        output_file = self.output_path / 'annotations_per_image.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Annotations per image chart saved to: {output_file}")
        return str(output_file)

    def generate_all_visualizations(self) -> List[str]:
        """Generate all enhanced visualizations."""
        logger.info("Generating enhanced visualizations...")

        generated_files = []

        if chart := self.generate_split_comparison_chart():
            generated_files.append(chart)

        if chart := self.generate_split_pie_charts():
            generated_files.append(chart)

        if chart := self.generate_class_balance_heatmap():
            generated_files.append(chart)

        if chart := self.generate_bbox_analysis_chart():
            generated_files.append(chart)

        if chart := self.generate_sample_comparison_grid():
            generated_files.append(chart)

        if chart := self.generate_annotations_per_image_chart():
            generated_files.append(chart)

        logger.info(f"Generated {len(generated_files)} visualization files")
        return generated_files


def verify_splits(dataset_path: str, auto_fix: bool = False) -> SplitVerificationResult:
    """
    Convenience function to verify dataset splits.

    Args:
        dataset_path: Path to dataset root
        auto_fix: Whether to automatically fix issues

    Returns:
        SplitVerificationResult
    """
    verifier = DatasetSplitVerifier(dataset_path)
    result = verifier.verify_all()

    if auto_fix and result.total_errors > 0:
        verifier.auto_fix()

    return result


def generate_enhanced_reports(dataset_path: str) -> List[str]:
    """Generate all enhanced visualizations and reports."""
    visualizer = EnhancedDatasetVisualizer(dataset_path)
    return visualizer.generate_all_visualizations()


if __name__ == "__main__":
    import sys

    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "."
    auto_fix = "--fix" in sys.argv

    print("\n" + "=" * 70)
    print("YOLO DATASET SPLIT VERIFIER")
    print("=" * 70)

    # Run verification
    result = verify_splits(dataset_path, auto_fix=auto_fix)

    # Generate enhanced visualizations
    print("\nGenerating enhanced visualizations...")
    files = generate_enhanced_reports(dataset_path)

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    print(f"Reports saved to: {Path(dataset_path) / 'reports'}")
