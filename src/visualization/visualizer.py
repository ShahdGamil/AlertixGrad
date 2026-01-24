"""
Visualization and Analysis Module for YOLO Ensemble Pipeline
Generates comprehensive visualizations and dataset insights
"""

import cv2
import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from tqdm import tqdm


class YOLODatasetVisualizer:
    """Visualize and analyze YOLO dataset"""

    def __init__(self, logger, config: dict):
        self.logger = logger
        self.config = config

        # Visualization settings
        self.save_path = Path(config.get('save_path', 'outputs/visualizations'))
        self.save_path.mkdir(parents=True, exist_ok=True)

        self.class_names = config.get('classes', [])
        self.dpi = config.get('dpi', 150)
        self.figsize = tuple(config.get('figsize', [12, 8]))

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = self.dpi

    def generate_all_visualizations(
        self,
        images_dir: Path,
        labels_dir: Path,
        split_stats: Dict = None
    ):
        """Generate all visualizations"""
        self.logger.section("Generating Visualizations")

        images_dir = Path(images_dir)
        labels_dir = Path(labels_dir)

        # 1. Class distribution
        self.plot_class_distribution(labels_dir)

        # 2. Bounding box statistics
        self.plot_bbox_statistics(labels_dir)

        # 3. Image resolution statistics
        self.plot_image_resolution(images_dir)

        # 4. Sample grid
        self.plot_sample_grid(images_dir, labels_dir)

        # 5. Split statistics (if provided)
        if split_stats:
            self.plot_split_statistics(split_stats)

        self.logger.success("All visualizations generated")

    def plot_class_distribution(self, labels_dir: Path):
        """Plot class distribution bar chart"""
        self.logger.info("Plotting class distribution")

        # Count classes
        class_counts = self._count_classes(labels_dir)

        # Create plot
        fig, ax = plt.subplots(figsize=self.figsize)

        classes = [self.class_names[i] for i in sorted(class_counts.keys())]
        counts = [class_counts[i] for i in sorted(class_counts.keys())]

        bars = ax.bar(classes, counts, color='skyblue', edgecolor='navy', alpha=0.7)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold'
            )

        ax.set_xlabel('Class', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Instances', fontsize=12, fontweight='bold')
        ax.set_title('Class Distribution', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save
        output_path = self.save_path / 'class_distribution.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved: {output_path}")

    def plot_bbox_statistics(self, labels_dir: Path):
        """Plot bounding box size and aspect ratio statistics"""
        self.logger.info("Plotting bbox statistics")

        # Collect bbox stats
        widths, heights, areas, aspect_ratios = self._collect_bbox_stats(labels_dir)

        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Width distribution
        axes[0, 0].hist(widths, bins=50, color='skyblue', edgecolor='navy', alpha=0.7)
        axes[0, 0].set_xlabel('Width (normalized)', fontweight='bold')
        axes[0, 0].set_ylabel('Frequency', fontweight='bold')
        axes[0, 0].set_title('Bounding Box Width Distribution', fontweight='bold')

        # Height distribution
        axes[0, 1].hist(heights, bins=50, color='lightcoral', edgecolor='darkred', alpha=0.7)
        axes[0, 1].set_xlabel('Height (normalized)', fontweight='bold')
        axes[0, 1].set_ylabel('Frequency', fontweight='bold')
        axes[0, 1].set_title('Bounding Box Height Distribution', fontweight='bold')

        # Area distribution
        axes[1, 0].hist(areas, bins=50, color='lightgreen', edgecolor='darkgreen', alpha=0.7)
        axes[1, 0].set_xlabel('Area (normalized)', fontweight='bold')
        axes[1, 0].set_ylabel('Frequency', fontweight='bold')
        axes[1, 0].set_title('Bounding Box Area Distribution', fontweight='bold')

        # Aspect ratio distribution
        axes[1, 1].hist(aspect_ratios, bins=50, color='plum', edgecolor='purple', alpha=0.7)
        axes[1, 1].set_xlabel('Aspect Ratio (W/H)', fontweight='bold')
        axes[1, 1].set_ylabel('Frequency', fontweight='bold')
        axes[1, 1].set_title('Bounding Box Aspect Ratio Distribution', fontweight='bold')

        plt.tight_layout()

        # Save
        output_path = self.save_path / 'bbox_statistics.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved: {output_path}")

    def plot_image_resolution(self, images_dir: Path):
        """Plot image resolution statistics"""
        self.logger.info("Plotting image resolution statistics")

        # Collect resolution stats
        resolutions = self._collect_image_resolutions(images_dir)

        widths = [r[0] for r in resolutions]
        heights = [r[1] for r in resolutions]

        # Create plot
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Width distribution
        axes[0].hist(widths, bins=30, color='skyblue', edgecolor='navy', alpha=0.7)
        axes[0].set_xlabel('Width (pixels)', fontweight='bold')
        axes[0].set_ylabel('Frequency', fontweight='bold')
        axes[0].set_title('Image Width Distribution', fontweight='bold')

        # Height distribution
        axes[1].hist(heights, bins=30, color='lightcoral', edgecolor='darkred', alpha=0.7)
        axes[1].set_xlabel('Height (pixels)', fontweight='bold')
        axes[1].set_ylabel('Frequency', fontweight='bold')
        axes[1].set_title('Image Height Distribution', fontweight='bold')

        plt.tight_layout()

        # Save
        output_path = self.save_path / 'image_resolution.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved: {output_path}")

    def plot_sample_grid(
        self,
        images_dir: Path,
        labels_dir: Path,
        grid_size: Tuple[int, int] = (4, 4)
    ):
        """Plot grid of sample images with annotations"""
        self.logger.info("Plotting sample grid")

        # Get random samples
        image_files = self._get_image_files(images_dir)
        samples = random.sample(image_files, min(grid_size[0] * grid_size[1], len(image_files)))

        # Create grid
        fig, axes = plt.subplots(grid_size[0], grid_size[1], figsize=(16, 16))
        axes = axes.flatten()

        for idx, img_path in enumerate(samples):
            # Read image
            image = cv2.imread(str(img_path))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Read and draw annotations
            label_path = labels_dir / f"{img_path.stem}.txt"
            if label_path.exists():
                image = self._draw_annotations(image, label_path)

            axes[idx].imshow(image)
            axes[idx].axis('off')
            axes[idx].set_title(img_path.stem[:20], fontsize=8)

        plt.tight_layout()

        # Save
        output_path = self.save_path / 'sample_grid.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved: {output_path}")

    def plot_split_statistics(self, split_stats: Dict):
        """Plot train/val/test split statistics"""
        self.logger.info("Plotting split statistics")

        # Create subplots
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Split size distribution
        splits = ['Train', 'Val', 'Test']
        counts = [
            split_stats.get('train_count', 0),
            split_stats.get('val_count', 0),
            split_stats.get('test_count', 0)
        ]

        colors = ['#4CAF50', '#2196F3', '#FF9800']
        bars = axes[0].bar(splits, counts, color=colors, edgecolor='black', alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            axes[0].text(
                bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold'
            )

        axes[0].set_ylabel('Number of Samples', fontweight='bold')
        axes[0].set_title('Dataset Split Distribution', fontweight='bold')

        # Class distribution per split
        train_dist = split_stats.get('train_class_dist', {})
        val_dist = split_stats.get('val_class_dist', {})
        test_dist = split_stats.get('test_class_dist', {})

        class_ids = sorted(set(list(train_dist.keys()) + list(val_dist.keys()) + list(test_dist.keys())))

        x = np.arange(len(class_ids))
        width = 0.25

        train_counts = [train_dist.get(c, 0) for c in class_ids]
        val_counts = [val_dist.get(c, 0) for c in class_ids]
        test_counts = [test_dist.get(c, 0) for c in class_ids]

        axes[1].bar(x - width, train_counts, width, label='Train', color=colors[0], alpha=0.7)
        axes[1].bar(x, val_counts, width, label='Val', color=colors[1], alpha=0.7)
        axes[1].bar(x + width, test_counts, width, label='Test', color=colors[2], alpha=0.7)

        axes[1].set_xlabel('Class', fontweight='bold')
        axes[1].set_ylabel('Number of Samples', fontweight='bold')
        axes[1].set_title('Class Distribution by Split', fontweight='bold')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels([self.class_names[c] for c in class_ids], rotation=45, ha='right')
        axes[1].legend()

        plt.tight_layout()

        # Save
        output_path = self.save_path / 'split_statistics.png'
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved: {output_path}")

    def _count_classes(self, labels_dir: Path) -> Dict[int, int]:
        """Count instances per class"""
        class_counts = Counter()

        for label_file in labels_dir.glob('*.txt'):
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        class_id = int(parts[0])
                        class_counts[class_id] += 1

        return dict(class_counts)

    def _collect_bbox_stats(self, labels_dir: Path) -> Tuple[List, List, List, List]:
        """Collect bounding box statistics"""
        widths, heights, areas, aspect_ratios = [], [], [], []

        for label_file in labels_dir.glob('*.txt'):
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        w = float(parts[3])
                        h = float(parts[4])
                        widths.append(w)
                        heights.append(h)
                        areas.append(w * h)
                        if h > 0:
                            aspect_ratios.append(w / h)

        return widths, heights, areas, aspect_ratios

    def _collect_image_resolutions(self, images_dir: Path) -> List[Tuple[int, int]]:
        """Collect image resolutions"""
        resolutions = []
        image_files = self._get_image_files(images_dir)

        for img_path in image_files:
            img = cv2.imread(str(img_path))
            if img is not None:
                h, w = img.shape[:2]
                resolutions.append((w, h))

        return resolutions

    def _draw_annotations(self, image: np.ndarray, label_path: Path) -> np.ndarray:
        """Draw bounding boxes on image"""
        h, w = image.shape[:2]

        # Define colors for each class
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]

        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    x_center = float(parts[1]) * w
                    y_center = float(parts[2]) * h
                    width = float(parts[3]) * w
                    height = float(parts[4]) * h

                    x1 = int(x_center - width / 2)
                    y1 = int(y_center - height / 2)
                    x2 = int(x_center + width / 2)
                    y2 = int(y_center + height / 2)

                    color = colors[class_id % len(colors)]

                    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

                    label = self.class_names[class_id] if class_id < len(self.class_names) else str(class_id)
                    cv2.putText(
                        image, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                    )

        return image

    def _get_image_files(self, images_dir: Path) -> List[Path]:
        """Get all image files"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []

        for ext in image_extensions:
            image_files.extend(images_dir.glob(f'*{ext}'))
            image_files.extend(images_dir.glob(f'*{ext.upper()}'))

        return sorted(image_files)
