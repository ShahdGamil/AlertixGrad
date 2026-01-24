"""
Dataset Splitting Module for YOLO Ensemble Pipeline
Stratified train/val/test split with no data leakage
"""

import shutil
import random
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from tqdm import tqdm


class YOLODatasetSplitter:
    """Split dataset into train/val/test with stratification"""

    def __init__(self, logger, config: dict):
        self.logger = logger
        self.config = config

        # Split settings
        self.train_ratio = config.get('train_ratio', 0.7)
        self.val_ratio = config.get('val_ratio', 0.2)
        self.test_ratio = config.get('test_ratio', 0.1)
        self.stratified = config.get('stratified', True)
        self.shuffle = config.get('shuffle', True)
        self.random_seed = config.get('random_seed', 42)

        # Validate ratios
        total = self.train_ratio + self.val_ratio + self.test_ratio
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Split ratios must sum to 1.0, got {total}")

        # Set random seed
        random.seed(self.random_seed)

        # Results
        self.results = {
            'train_count': 0,
            'val_count': 0,
            'test_count': 0,
            'train_class_dist': {},
            'val_class_dist': {},
            'test_class_dist': {}
        }

    def split_dataset(
        self,
        input_images_dir: Path,
        input_labels_dir: Path,
        output_dir: Path
    ) -> Dict:
        """
        Split dataset into train/val/test

        Args:
            input_images_dir: Input images directory
            input_labels_dir: Input labels directory
            output_dir: Output base directory

        Returns:
            Split statistics
        """
        self.logger.section("Dataset Splitting")

        input_images_dir = Path(input_images_dir)
        input_labels_dir = Path(input_labels_dir)
        output_dir = Path(output_dir)

        # Create output structure
        for split in ['train', 'val', 'test']:
            (output_dir / split / 'images').mkdir(parents=True, exist_ok=True)
            (output_dir / split / 'labels').mkdir(parents=True, exist_ok=True)

        # Get all samples
        samples = self._get_samples(input_images_dir, input_labels_dir)

        self.logger.info(f"Total samples: {len(samples)}")

        # Stratified split
        if self.stratified:
            train, val, test = self._stratified_split(samples)
        else:
            train, val, test = self._random_split(samples)

        # Copy files to splits
        self._copy_split(train, output_dir / 'train', 'Train')
        self._copy_split(val, output_dir / 'val', 'Validation')
        self._copy_split(test, output_dir / 'test', 'Test')

        # Analyze class distribution
        self.results['train_count'] = len(train)
        self.results['val_count'] = len(val)
        self.results['test_count'] = len(test)

        self.results['train_class_dist'] = self._get_class_distribution(train)
        self.results['val_class_dist'] = self._get_class_distribution(val)
        self.results['test_class_dist'] = self._get_class_distribution(test)

        # Generate summary
        summary = self._generate_summary()

        return summary

    def _get_samples(
        self,
        images_dir: Path,
        labels_dir: Path
    ) -> List[Dict]:
        """Get all valid image-label pairs"""
        samples = []
        image_files = self._get_image_files(images_dir)

        for img_path in image_files:
            label_path = labels_dir / f"{img_path.stem}.txt"

            if not label_path.exists():
                continue

            # Read primary class from label
            primary_class = self._get_primary_class(label_path)

            samples.append({
                'image_path': img_path,
                'label_path': label_path,
                'primary_class': primary_class
            })

        return samples

    def _get_primary_class(self, label_path: Path) -> int:
        """Get primary (first) class from label file"""
        with open(label_path, 'r') as f:
            first_line = f.readline().strip()

        if first_line:
            parts = first_line.split()
            return int(parts[0])

        return -1

    def _stratified_split(
        self,
        samples: List[Dict]
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Perform stratified split by class"""

        # Group samples by class
        class_samples = defaultdict(list)
        for sample in samples:
            class_samples[sample['primary_class']].append(sample)

        train_samples = []
        val_samples = []
        test_samples = []

        # Split each class separately
        for class_id, class_samp in class_samples.items():
            if self.shuffle:
                random.shuffle(class_samp)

            n_samples = len(class_samp)
            n_train = int(n_samples * self.train_ratio)
            n_val = int(n_samples * self.val_ratio)

            train_samples.extend(class_samp[:n_train])
            val_samples.extend(class_samp[n_train:n_train+n_val])
            test_samples.extend(class_samp[n_train+n_val:])

        # Shuffle combined splits
        if self.shuffle:
            random.shuffle(train_samples)
            random.shuffle(val_samples)
            random.shuffle(test_samples)

        return train_samples, val_samples, test_samples

    def _random_split(
        self,
        samples: List[Dict]
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Perform random split"""

        if self.shuffle:
            random.shuffle(samples)

        n_samples = len(samples)
        n_train = int(n_samples * self.train_ratio)
        n_val = int(n_samples * self.val_ratio)

        train = samples[:n_train]
        val = samples[n_train:n_train+n_val]
        test = samples[n_train+n_val:]

        return train, val, test

    def _copy_split(
        self,
        samples: List[Dict],
        output_dir: Path,
        split_name: str
    ):
        """Copy samples to split directory"""

        self.logger.info(f"Copying {len(samples)} samples to {split_name}")

        for sample in tqdm(samples, desc=f"Copying {split_name}", leave=False):
            img_path = sample['image_path']
            label_path = sample['label_path']

            # Copy image
            dst_img = output_dir / 'images' / img_path.name
            shutil.copy2(img_path, dst_img)

            # Copy label
            dst_label = output_dir / 'labels' / label_path.name
            shutil.copy2(label_path, dst_label)

    def _get_class_distribution(self, samples: List[Dict]) -> Dict[int, int]:
        """Get class distribution for samples"""
        distribution = defaultdict(int)

        for sample in samples:
            distribution[sample['primary_class']] += 1

        return dict(distribution)

    def _get_image_files(self, images_dir: Path) -> List[Path]:
        """Get all image files"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []

        for ext in image_extensions:
            image_files.extend(images_dir.glob(f'*{ext}'))
            image_files.extend(images_dir.glob(f'*{ext.upper()}'))

        return sorted(image_files)

    def _generate_summary(self) -> Dict:
        """Generate split summary"""
        self.logger.subsection("Split Summary")

        total = (
            self.results['train_count'] +
            self.results['val_count'] +
            self.results['test_count']
        )

        summary = {
            'total_samples': total,
            'train_count': self.results['train_count'],
            'val_count': self.results['val_count'],
            'test_count': self.results['test_count'],
            'train_ratio': self.results['train_count'] / total if total > 0 else 0,
            'val_ratio': self.results['val_count'] / total if total > 0 else 0,
            'test_ratio': self.results['test_count'] / total if total > 0 else 0,
            'train_class_dist': self.results['train_class_dist'],
            'val_class_dist': self.results['val_class_dist'],
            'test_class_dist': self.results['test_class_dist']
        }

        self.logger.info(f"Total: {total}")
        self.logger.info(f"Train: {summary['train_count']} ({summary['train_ratio']:.1%})")
        self.logger.info(f"Val: {summary['val_count']} ({summary['val_ratio']:.1%})")
        self.logger.info(f"Test: {summary['test_count']} ({summary['test_ratio']:.1%})")

        self.logger.success("Dataset split completed")

        return summary
