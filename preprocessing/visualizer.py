"""
Visualization and Reporting Module for YOLO Format Dataset
Generates charts, sample grids, and comprehensive analysis reports.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
import random

# Optional imports with fallbacks
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server/headless
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not installed. Charts will not be generated.")

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: PIL not installed. Image grids will not be generated.")

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class DatasetStats:
    """Comprehensive dataset statistics."""
    total_images: int = 0
    total_annotations: int = 0
    class_distribution: Dict[int, int] = field(default_factory=dict)
    images_per_split: Dict[str, int] = field(default_factory=dict)
    bbox_sizes: List[Tuple[float, float]] = field(default_factory=list)
    image_sizes: List[Tuple[int, int]] = field(default_factory=list)
    annotations_per_image: List[int] = field(default_factory=list)
    split_class_distribution: Dict[str, Dict[int, int]] = field(default_factory=dict)


class DatasetVisualizer:
    """
    Generates visualizations and reports for YOLO format dataset.
    Optimized for retail theft detection analysis.
    """

    # Class colors for visualization (BGR for OpenCV compatibility)
    CLASS_COLORS = [
        (255, 0, 0),      # Customer-Bagpack - Red
        (0, 255, 0),      # Product - Green
        (0, 0, 255),      # Product-Picked - Blue
        (255, 255, 0),    # Shopping-Cart - Cyan
        (255, 0, 255),    # normal - Magenta
        (0, 165, 255),    # theft - Orange
    ]

    CLASS_NAMES = ['Customer-Bagpack', 'Product', 'Product-Picked',
                   'Shopping-Cart', 'normal', 'theft']

    def __init__(self, dataset_path: str, output_path: Optional[str] = None):
        """
        Initialize visualizer.

        Args:
            dataset_path: Root path of the dataset
            output_path: Path for output visualizations (default: dataset_path/reports)
        """
        self.dataset_path = Path(dataset_path)
        self.output_path = Path(output_path) if output_path else self.dataset_path / 'reports'
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.stats = DatasetStats()

    def analyze_dataset(self) -> DatasetStats:
        """Collect comprehensive dataset statistics."""
        logger.info("Analyzing dataset...")

        for split in ['train', 'valid', 'test']:
            split_path = self.dataset_path / split
            if not split_path.exists():
                continue

            images_path = split_path / 'images'
            labels_path = split_path / 'labels'

            if not images_path.exists() or not labels_path.exists():
                continue

            split_class_counts = defaultdict(int)
            image_count = 0

            for label_file in labels_path.glob('*.txt'):
                # Find corresponding image
                img_path = None
                for ext in ['.jpg', '.jpeg', '.png']:
                    candidate = images_path / f"{label_file.stem}{ext}"
                    if candidate.exists():
                        img_path = candidate
                        break

                if not img_path:
                    continue

                image_count += 1

                # Get image size
                try:
                    if HAS_PIL:
                        with Image.open(img_path) as img:
                            self.stats.image_sizes.append((img.width, img.height))
                except:
                    pass

                # Parse labels
                content = label_file.read_text().strip()
                annotations = 0

                if content:
                    for line in content.split('\n'):
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            try:
                                class_id = int(parts[0])
                                width = float(parts[3])
                                height = float(parts[4])

                                self.stats.class_distribution[class_id] = \
                                    self.stats.class_distribution.get(class_id, 0) + 1
                                split_class_counts[class_id] += 1
                                self.stats.bbox_sizes.append((width, height))
                                annotations += 1
                            except ValueError:
                                continue

                self.stats.annotations_per_image.append(annotations)

            self.stats.images_per_split[split] = image_count
            self.stats.split_class_distribution[split] = dict(split_class_counts)
            self.stats.total_images += image_count

        self.stats.total_annotations = sum(self.stats.class_distribution.values())
        return self.stats

    def generate_class_distribution_chart(self) -> Optional[str]:
        """Generate class distribution bar chart."""
        if not HAS_MATPLOTLIB:
            logger.warning("matplotlib not available, skipping chart generation")
            return None

        if not self.stats.class_distribution:
            self.analyze_dataset()

        fig, ax = plt.subplots(figsize=(12, 6))

        classes = sorted(self.stats.class_distribution.keys())
        counts = [self.stats.class_distribution[c] for c in classes]
        names = [self.CLASS_NAMES[c] if c < len(self.CLASS_NAMES) else f"Class_{c}" for c in classes]
        colors = [f'#{r:02x}{g:02x}{b:02x}' for r, g, b in
                  [self.CLASS_COLORS[c] if c < len(self.CLASS_COLORS) else (128, 128, 128) for c in classes]]

        bars = ax.bar(names, counts, color=colors, edgecolor='black', linewidth=1.2)

        # Add value labels on bars
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                    str(count), ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_xlabel('Class', fontsize=12)
        ax.set_ylabel('Number of Instances', fontsize=12)
        ax.set_title('Class Distribution in Dataset', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)

        # Add grid
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        ax.set_axisbelow(True)

        plt.tight_layout()
        output_file = self.output_path / 'class_distribution.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Class distribution chart saved to: {output_file}")
        return str(output_file)

    def generate_bbox_size_distribution(self) -> Optional[str]:
        """Generate bounding box size distribution chart."""
        if not HAS_MATPLOTLIB or not HAS_NUMPY:
            logger.warning("matplotlib/numpy not available, skipping chart generation")
            return None

        if not self.stats.bbox_sizes:
            self.analyze_dataset()

        widths = [s[0] for s in self.stats.bbox_sizes]
        heights = [s[1] for s in self.stats.bbox_sizes]

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Width distribution
        axes[0].hist(widths, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        axes[0].set_xlabel('Normalized Width')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('Bounding Box Width Distribution')
        axes[0].axvline(np.mean(widths), color='red', linestyle='--', label=f'Mean: {np.mean(widths):.3f}')
        axes[0].legend()

        # Height distribution
        axes[1].hist(heights, bins=50, color='coral', edgecolor='black', alpha=0.7)
        axes[1].set_xlabel('Normalized Height')
        axes[1].set_ylabel('Frequency')
        axes[1].set_title('Bounding Box Height Distribution')
        axes[1].axvline(np.mean(heights), color='red', linestyle='--', label=f'Mean: {np.mean(heights):.3f}')
        axes[1].legend()

        # Scatter plot of width vs height
        axes[2].scatter(widths, heights, alpha=0.3, s=10, c='purple')
        axes[2].set_xlabel('Normalized Width')
        axes[2].set_ylabel('Normalized Height')
        axes[2].set_title('Width vs Height Distribution')
        axes[2].set_xlim(0, 1)
        axes[2].set_ylim(0, 1)

        plt.tight_layout()
        output_file = self.output_path / 'bbox_size_distribution.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Bbox size distribution saved to: {output_file}")
        return str(output_file)

    def generate_image_resolution_chart(self) -> Optional[str]:
        """Generate image resolution distribution chart."""
        if not HAS_MATPLOTLIB or not HAS_NUMPY:
            logger.warning("matplotlib/numpy not available, skipping chart generation")
            return None

        if not self.stats.image_sizes:
            self.analyze_dataset()

        widths = [s[0] for s in self.stats.image_sizes]
        heights = [s[1] for s in self.stats.image_sizes]

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Resolution scatter
        axes[0].scatter(widths, heights, alpha=0.5, s=20, c='teal')
        axes[0].set_xlabel('Width (pixels)')
        axes[0].set_ylabel('Height (pixels)')
        axes[0].set_title('Image Resolution Distribution')

        # Resolution histogram (by aspect ratio)
        aspect_ratios = [w/h for w, h in zip(widths, heights)]
        axes[1].hist(aspect_ratios, bins=30, color='orange', edgecolor='black', alpha=0.7)
        axes[1].set_xlabel('Aspect Ratio (Width/Height)')
        axes[1].set_ylabel('Frequency')
        axes[1].set_title('Aspect Ratio Distribution')
        axes[1].axvline(1.0, color='red', linestyle='--', label='1:1 Ratio')
        axes[1].legend()

        plt.tight_layout()
        output_file = self.output_path / 'image_resolution_distribution.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Image resolution chart saved to: {output_file}")
        return str(output_file)

    def generate_split_statistics_chart(self) -> Optional[str]:
        """Generate train/val/test split statistics chart."""
        if not HAS_MATPLOTLIB:
            logger.warning("matplotlib not available, skipping chart generation")
            return None

        if not self.stats.split_class_distribution:
            self.analyze_dataset()

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Images per split (pie chart)
        splits = list(self.stats.images_per_split.keys())
        counts = list(self.stats.images_per_split.values())
        colors = ['#2ecc71', '#3498db', '#e74c3c']

        axes[0].pie(counts, labels=splits, autopct='%1.1f%%', colors=colors[:len(splits)],
                    explode=[0.02] * len(splits), shadow=True, startangle=90)
        axes[0].set_title('Images per Split', fontsize=12, fontweight='bold')

        # Class distribution per split (grouped bar chart)
        x = np.arange(len(self.CLASS_NAMES))
        width = 0.25

        for i, split in enumerate(['train', 'valid', 'test']):
            if split in self.stats.split_class_distribution:
                counts = [self.stats.split_class_distribution[split].get(c, 0) for c in range(len(self.CLASS_NAMES))]
                axes[1].bar(x + i * width, counts, width, label=split.capitalize(),
                           color=colors[i], edgecolor='black', linewidth=0.5)

        axes[1].set_xlabel('Class')
        axes[1].set_ylabel('Count')
        axes[1].set_title('Class Distribution per Split', fontsize=12, fontweight='bold')
        axes[1].set_xticks(x + width)
        axes[1].set_xticklabels(self.CLASS_NAMES, rotation=45, ha='right')
        axes[1].legend()
        axes[1].yaxis.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        output_file = self.output_path / 'split_statistics.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Split statistics chart saved to: {output_file}")
        return str(output_file)

    def generate_sample_grid(self, num_samples: int = 9, split: str = 'train') -> Optional[str]:
        """Generate a grid of sample labeled images."""
        if not HAS_PIL:
            logger.warning("PIL not available, skipping sample grid generation")
            return None

        images_path = self.dataset_path / split / 'images'
        labels_path = self.dataset_path / split / 'labels'

        if not images_path.exists() or not labels_path.exists():
            logger.warning(f"Split {split} not found")
            return None

        # Get random sample of images
        image_files = list(images_path.glob('*.jpg')) + list(images_path.glob('*.png'))
        if len(image_files) < num_samples:
            num_samples = len(image_files)

        random.seed(42)
        samples = random.sample(image_files, num_samples)

        # Calculate grid dimensions
        cols = int(np.ceil(np.sqrt(num_samples)))
        rows = int(np.ceil(num_samples / cols))

        # Target size for each cell
        cell_size = 320
        grid_width = cols * cell_size
        grid_height = rows * cell_size

        grid_image = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))
        draw = ImageDraw.Draw(grid_image)

        for idx, img_path in enumerate(samples):
            row = idx // cols
            col = idx % cols

            try:
                # Load and resize image
                img = Image.open(img_path).convert('RGB')
                orig_w, orig_h = img.size

                # Calculate resize with aspect ratio
                scale = min(cell_size / orig_w, cell_size / orig_h)
                new_w, new_h = int(orig_w * scale), int(orig_h * scale)
                img_resized = img.resize((new_w, new_h), Image.BILINEAR)

                # Create cell with padding
                cell = Image.new('RGB', (cell_size, cell_size), (240, 240, 240))
                offset_x = (cell_size - new_w) // 2
                offset_y = (cell_size - new_h) // 2
                cell.paste(img_resized, (offset_x, offset_y))

                # Draw bounding boxes
                cell_draw = ImageDraw.Draw(cell)
                label_path = labels_path / f"{img_path.stem}.txt"

                if label_path.exists():
                    content = label_path.read_text().strip()
                    if content:
                        for line in content.split('\n'):
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                try:
                                    class_id = int(parts[0])
                                    x_center = float(parts[1])
                                    y_center = float(parts[2])
                                    width = float(parts[3])
                                    height = float(parts[4])

                                    # Convert to pixel coordinates
                                    x1 = int((x_center - width/2) * new_w + offset_x)
                                    y1 = int((y_center - height/2) * new_h + offset_y)
                                    x2 = int((x_center + width/2) * new_w + offset_x)
                                    y2 = int((y_center + height/2) * new_h + offset_y)

                                    color = self.CLASS_COLORS[class_id] if class_id < len(self.CLASS_COLORS) else (128, 128, 128)
                                    cell_draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

                                    # Add class label
                                    label = self.CLASS_NAMES[class_id] if class_id < len(self.CLASS_NAMES) else f"C{class_id}"
                                    cell_draw.text((x1, y1 - 12), label[:10], fill=color)
                                except:
                                    continue

                # Paste cell into grid
                grid_image.paste(cell, (col * cell_size, row * cell_size))

            except Exception as e:
                logger.warning(f"Error processing {img_path.name}: {e}")

        output_file = self.output_path / f'sample_grid_{split}.png'
        grid_image.save(output_file, quality=95)
        logger.info(f"Sample grid saved to: {output_file}")
        return str(output_file)

    def generate_summary_report(self) -> dict:
        """Generate comprehensive dataset summary report."""
        if not self.stats.class_distribution:
            self.analyze_dataset()

        report = {
            'generated_at': datetime.now().isoformat(),
            'dataset_path': str(self.dataset_path),
            'summary': {
                'total_images': self.stats.total_images,
                'total_annotations': self.stats.total_annotations,
                'average_annotations_per_image': round(
                    np.mean(self.stats.annotations_per_image) if self.stats.annotations_per_image else 0, 2
                ),
                'splits': self.stats.images_per_split
            },
            'class_distribution': {
                self.CLASS_NAMES[k] if k < len(self.CLASS_NAMES) else f"Class_{k}": v
                for k, v in sorted(self.stats.class_distribution.items())
            },
            'class_percentages': {
                self.CLASS_NAMES[k] if k < len(self.CLASS_NAMES) else f"Class_{k}": round(v / self.stats.total_annotations * 100, 2)
                for k, v in sorted(self.stats.class_distribution.items())
            } if self.stats.total_annotations > 0 else {},
            'bbox_statistics': {
                'avg_width': round(np.mean([s[0] for s in self.stats.bbox_sizes]), 4) if self.stats.bbox_sizes else 0,
                'avg_height': round(np.mean([s[1] for s in self.stats.bbox_sizes]), 4) if self.stats.bbox_sizes else 0,
                'min_width': round(min([s[0] for s in self.stats.bbox_sizes]), 4) if self.stats.bbox_sizes else 0,
                'min_height': round(min([s[1] for s in self.stats.bbox_sizes]), 4) if self.stats.bbox_sizes else 0,
                'max_width': round(max([s[0] for s in self.stats.bbox_sizes]), 4) if self.stats.bbox_sizes else 0,
                'max_height': round(max([s[1] for s in self.stats.bbox_sizes]), 4) if self.stats.bbox_sizes else 0,
            },
            'image_statistics': {
                'resolutions': list(set(self.stats.image_sizes))[:10],  # Show up to 10 unique resolutions
                'most_common_resolution': max(set(self.stats.image_sizes), key=self.stats.image_sizes.count) if self.stats.image_sizes else None
            },
            'split_details': self.stats.split_class_distribution,
            'quality_assessment': self._assess_quality(),
            'recommendations': self._generate_recommendations()
        }

        # Save report
        report_file = self.output_path / 'dataset_summary_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Summary report saved to: {report_file}")
        return report

    def _assess_quality(self) -> dict:
        """Assess dataset quality."""
        issues = []
        score = 100

        # Check class imbalance
        if self.stats.class_distribution:
            max_count = max(self.stats.class_distribution.values())
            min_count = min(self.stats.class_distribution.values())
            imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')

            if imbalance_ratio > 20:
                issues.append("Severe class imbalance detected (ratio > 20:1)")
                score -= 20
            elif imbalance_ratio > 10:
                issues.append("Significant class imbalance detected (ratio > 10:1)")
                score -= 10
            elif imbalance_ratio > 5:
                issues.append("Moderate class imbalance detected (ratio > 5:1)")
                score -= 5

        # Check for small bboxes
        if self.stats.bbox_sizes:
            small_boxes = sum(1 for w, h in self.stats.bbox_sizes if w < 0.02 or h < 0.02)
            small_ratio = small_boxes / len(self.stats.bbox_sizes)
            if small_ratio > 0.1:
                issues.append(f"{small_ratio:.1%} of bboxes are very small (<2% of image)")
                score -= 10

        # Check split sizes
        if self.stats.images_per_split:
            total = sum(self.stats.images_per_split.values())
            train_ratio = self.stats.images_per_split.get('train', 0) / total if total > 0 else 0
            if train_ratio < 0.6:
                issues.append("Training set is smaller than recommended (< 60%)")
                score -= 10

        # Check total dataset size
        if self.stats.total_images < 1000:
            issues.append("Dataset is relatively small (< 1000 images)")
            score -= 5

        return {
            'score': max(0, score),
            'rating': 'Excellent' if score >= 90 else 'Good' if score >= 70 else 'Fair' if score >= 50 else 'Needs Improvement',
            'issues': issues
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate training recommendations."""
        recommendations = []

        # Based on class distribution
        if self.stats.class_distribution:
            theft_count = self.stats.class_distribution.get(5, 0)
            normal_count = self.stats.class_distribution.get(4, 0)

            if theft_count < normal_count * 0.1:
                recommendations.append(
                    "Theft class is significantly underrepresented. Consider using focal loss with gamma=2.0"
                )

            if self.stats.class_distribution.get(3, 0) < 300:
                recommendations.append(
                    "Shopping-Cart has limited samples. Enable strong augmentation for this class"
                )

        # Based on bbox sizes
        if self.stats.bbox_sizes:
            avg_size = np.mean([w * h for w, h in self.stats.bbox_sizes])
            if avg_size < 0.05:
                recommendations.append(
                    "Many small objects detected. Consider using higher resolution (640x640 or higher)"
                )
            elif avg_size > 0.3:
                recommendations.append(
                    "Many large objects detected. Standard 640x640 should work well"
                )

        # General recommendations
        recommendations.extend([
            "Use mosaic augmentation (enabled by default in YOLOv8)",
            "Enable copy-paste augmentation for minority classes",
            "Consider using EMA (Exponential Moving Average) for stable training",
            "Monitor mAP@0.5 specifically for the Theft class during validation"
        ])

        return recommendations

    def generate_all_visualizations(self) -> List[str]:
        """Generate all visualizations and reports."""
        logger.info("Generating all visualizations...")

        generated_files = []

        # Analyze first
        self.analyze_dataset()

        # Generate charts
        if chart := self.generate_class_distribution_chart():
            generated_files.append(chart)

        if chart := self.generate_bbox_size_distribution():
            generated_files.append(chart)

        if chart := self.generate_image_resolution_chart():
            generated_files.append(chart)

        if chart := self.generate_split_statistics_chart():
            generated_files.append(chart)

        # Generate sample grids
        for split in ['train', 'valid', 'test']:
            if grid := self.generate_sample_grid(num_samples=9, split=split):
                generated_files.append(grid)

        # Generate summary report
        report = self.generate_summary_report()
        generated_files.append(str(self.output_path / 'dataset_summary_report.json'))

        logger.info(f"Generated {len(generated_files)} visualization files")
        return generated_files


def visualize_dataset(dataset_path: str, output_path: Optional[str] = None) -> List[str]:
    """
    Convenience function to generate all visualizations.

    Args:
        dataset_path: Path to the dataset root
        output_path: Optional output path for visualizations

    Returns:
        List of generated file paths
    """
    visualizer = DatasetVisualizer(dataset_path, output_path)
    return visualizer.generate_all_visualizations()


if __name__ == "__main__":
    import sys
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "."
    files = visualize_dataset(dataset_path)
    print(f"Generated {len(files)} files")
