"""
Preprocessing Module for YOLO Ensemble Pipeline
YOLOv8-compatible preprocessing with letterbox padding
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple
from tqdm import tqdm


class YOLOPreprocessor:
    """Preprocess images for YOLOv8 training"""

    def __init__(self, logger, config: dict):
        self.logger = logger
        self.config = config

        # Preprocessing settings
        self.target_size = tuple(config.get('target_size', [640, 640]))
        self.maintain_aspect = config.get('maintain_aspect_ratio', True)
        self.letterbox = config.get('letterbox_padding', True)
        self.padding_color = tuple(config.get('padding_color', [114, 114, 114]))
        self.normalize = config.get('normalize_pixels', False)
        self.auto_orient = config.get('auto_orient', True)
        self.output_format = config.get('format', 'jpg')
        self.quality = config.get('quality', 95)

    def preprocess_dataset(
        self,
        input_images_dir: Path,
        output_images_dir: Path
    ):
        """Preprocess all images in dataset"""
        self.logger.section("Preprocessing Dataset")

        input_images_dir = Path(input_images_dir)
        output_images_dir = Path(output_images_dir)
        output_images_dir.mkdir(parents=True, exist_ok=True)

        # Get image files
        image_files = self._get_image_files(input_images_dir)
        self.logger.info(f"Preprocessing {len(image_files)} images")

        for img_path in tqdm(image_files, desc="Preprocessing"):
            # Read image
            image = cv2.imread(str(img_path))

            if image is None:
                continue

            # Preprocess
            processed = self.preprocess_image(image)

            # Save
            output_path = output_images_dir / f"{img_path.stem}.{self.output_format}"
            cv2.imwrite(str(output_path), processed, [cv2.IMWRITE_JPEG_QUALITY, self.quality])

        self.logger.success("Preprocessing completed")

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess single image"""

        # Auto-orient if needed
        if self.auto_orient:
            image = self._auto_orient(image)

        # Resize with letterbox
        if self.letterbox and self.maintain_aspect:
            image = self._letterbox_resize(image, self.target_size, self.padding_color)
        else:
            image = cv2.resize(image, self.target_size)

        return image

    def _letterbox_resize(
        self,
        image: np.ndarray,
        target_size: Tuple[int, int],
        color: Tuple[int, int, int]
    ) -> np.ndarray:
        """Resize image with letterbox padding to maintain aspect ratio"""

        h, w = image.shape[:2]
        target_w, target_h = target_size

        # Calculate scale
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        # Resize
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Create canvas
        canvas = np.full((target_h, target_w, 3), color, dtype=np.uint8)

        # Calculate padding
        pad_w = (target_w - new_w) // 2
        pad_h = (target_h - new_h) // 2

        # Place resized image on canvas
        canvas[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = resized

        return canvas

    def _auto_orient(self, image: np.ndarray) -> np.ndarray:
        """Auto-orient image based on EXIF data"""
        # Basic implementation - can be enhanced with EXIF reading
        return image

    def _get_image_files(self, images_dir: Path):
        """Get all image files"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []

        for ext in image_extensions:
            image_files.extend(images_dir.glob(f'*{ext}'))
            image_files.extend(images_dir.glob(f'*{ext.upper()}'))

        return sorted(image_files)
