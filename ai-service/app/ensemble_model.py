"""
YOLOv8 Ensemble Model with Weighted Box Fusion
"""
import torch
import numpy as np
from ultralytics import YOLO
from ensemble_boxes import weighted_boxes_fusion
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import cv2

from .config import settings, CLASS_NAMES, get_severity

logger = logging.getLogger(__name__)


class YOLOv8Ensemble:
    """
    Ensemble of YOLOv8 models (n, s, m) with Weighted Box Fusion for improved detection
    """

    def __init__(self):
        """Initialize the ensemble of YOLOv8 models with graceful degradation"""
        self.models = []
        self.model_names = []
        self.active_weights = []
        self.device = settings.DEVICE if torch.cuda.is_available() else "cpu"

        logger.info(f"Initializing YOLOv8 Ensemble on device: {self.device}")

        # Try to load each model with graceful degradation
        model_configs = [
            ("yolov8n", settings.MODEL_YOLOV8N_PATH, 1.0),
            ("yolov8s", settings.MODEL_YOLOV8S_PATH, 0.3),
            ("yolov8m", settings.MODEL_YOLOV8M_PATH, 1.0)
        ]

        for name, path, weight in model_configs:
            try:
                model_path = Path(path)
                if not model_path.exists():
                    logger.warning(f"Model not found: {path} - skipping {name}")
                    continue

                logger.info(f"Loading {name} from {path}")
                model = YOLO(str(model_path))
                model.to(self.device)
                self.models.append(model)
                self.model_names.append(name)
                self.active_weights.append(weight)
                logger.info(f"✓ {name} loaded successfully")

            except Exception as e:
                logger.error(f"Failed to load {name}: {str(e)} - continuing with other models")
                continue

        if len(self.models) == 0:
            raise RuntimeError("No models could be loaded - ensemble requires at least one model")

        # Normalize weights based on active models
        total = sum(self.active_weights)
        self.weights = [w / total for w in self.active_weights]

        logger.info(f"✓ Ensemble initialized with {len(self.models)} model(s): {self.model_names}")
        logger.info(f"  Active weights: {self.weights}")

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for inference

        Args:
            image: Input image as numpy array (BGR format from cv2)

        Returns:
            Preprocessed image
        """
        # Image is already in BGR format from cv2
        # YOLO handles conversion internally
        return image

    def run_single_model_inference(
        self,
        model: YOLO,
        image: np.ndarray,
        conf_threshold: float = None,
        iou_threshold: float = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Run inference on a single model

        Args:
            model: YOLO model instance
            image: Preprocessed image
            conf_threshold: Confidence threshold
            iou_threshold: IOU threshold for NMS

        Returns:
            boxes, scores, labels as numpy arrays normalized to [0, 1]
        """
        conf_threshold = conf_threshold or settings.CONFIDENCE_THRESHOLD
        iou_threshold = iou_threshold or settings.IOU_THRESHOLD

        # Run inference
        results = model.predict(
            image,
            conf=conf_threshold,
            iou=iou_threshold,
            verbose=False,
            device=self.device
        )

        if len(results) == 0 or len(results[0].boxes) == 0:
            return np.array([]), np.array([]), np.array([])

        # Extract results
        boxes = results[0].boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
        scores = results[0].boxes.conf.cpu().numpy()
        labels = results[0].boxes.cls.cpu().numpy().astype(int)

        # Normalize boxes to [0, 1] for WBF
        img_h, img_w = image.shape[:2]
        boxes_norm = boxes.copy()
        boxes_norm[:, [0, 2]] /= img_w  # Normalize x coordinates
        boxes_norm[:, [1, 3]] /= img_h  # Normalize y coordinates

        return boxes_norm, scores, labels

    def apply_weighted_box_fusion(
        self,
        boxes_list: List[np.ndarray],
        scores_list: List[np.ndarray],
        labels_list: List[np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Apply Weighted Box Fusion to ensemble predictions

        Args:
            boxes_list: List of boxes from each model (normalized [0, 1])
            scores_list: List of scores from each model
            labels_list: List of labels from each model

        Returns:
            Fused boxes, scores, labels
        """
        if not boxes_list or all(len(b) == 0 for b in boxes_list):
            return np.array([]), np.array([]), np.array([])

        # Convert to lists of lists for WBF
        boxes_list = [b.tolist() if len(b) > 0 else [] for b in boxes_list]
        scores_list = [s.tolist() if len(s) > 0 else [] for s in scores_list]
        labels_list = [l.tolist() if len(l) > 0 else [] for l in labels_list]

        # Apply Weighted Box Fusion
        fused_boxes, fused_scores, fused_labels = weighted_boxes_fusion(
            boxes_list,
            scores_list,
            labels_list,
            weights=self.weights,
            iou_thr=settings.ENSEMBLE_IOU_THRESHOLD,
            skip_box_thr=settings.ENSEMBLE_SKIP_BOX_THRESHOLD
        )

        return fused_boxes, fused_scores, fused_labels.astype(int)

    def detect(
        self,
        image: np.ndarray,
        conf_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None,
        camera_id: Optional[str] = None
    ) -> Dict:
        """
        Run ensemble detection on an image

        Args:
            image: Input image as numpy array (BGR)
            conf_threshold: Confidence threshold (optional)
            iou_threshold: IOU threshold (optional)
            camera_id: Camera identifier (optional)

        Returns:
            Detection results as dictionary
        """
        try:
            # Preprocess
            processed_image = self.preprocess_image(image)
            img_h, img_w = image.shape[:2]

            # Run inference on all models
            all_boxes = []
            all_scores = []
            all_labels = []

            for model, name in zip(self.models, self.model_names):
                boxes, scores, labels = self.run_single_model_inference(
                    model,
                    processed_image,
                    conf_threshold,
                    iou_threshold
                )
                all_boxes.append(boxes)
                all_scores.append(scores)
                all_labels.append(labels)
                logger.debug(f"{name}: {len(boxes)} detections")

            # Apply Weighted Box Fusion
            fused_boxes, fused_scores, fused_labels = self.apply_weighted_box_fusion(
                all_boxes, all_scores, all_labels
            )

            # Denormalize boxes back to pixel coordinates
            if len(fused_boxes) > 0:
                fused_boxes[:, [0, 2]] *= img_w
                fused_boxes[:, [1, 3]] *= img_h

            # Determine if threat detected (6-class system)
            threat_classes = {"theft", "product_picked", "customer_bagpack"}
            threat_detected = len(fused_boxes) > 0 and any(
                CLASS_NAMES.get(int(label), "normal") in threat_classes
                for label in fused_labels
            )

            # Get dominant class and confidence
            if len(fused_scores) > 0:
                max_idx = np.argmax(fused_scores)
                dominant_class = CLASS_NAMES.get(int(fused_labels[max_idx]), "normal")
                max_confidence = float(fused_scores[max_idx])
                severity = get_severity(max_confidence, dominant_class)
            else:
                dominant_class = "normal"
                max_confidence = 0.0
                severity = "low"

            # Format bounding boxes
            bounding_boxes = []
            for box, score, label in zip(fused_boxes, fused_scores, fused_labels):
                bounding_boxes.append({
                    "label": CLASS_NAMES.get(int(label), f"class_{int(label)}"),
                    "confidence": float(score),
                    "x_min": int(box[0]),
                    "y_min": int(box[1]),
                    "x_max": int(box[2]),
                    "y_max": int(box[3]),
                    "width": int(box[2] - box[0]),
                    "height": int(box[3] - box[1])
                })

            # Build response
            response = {
                "event": dominant_class + "_detected" if threat_detected else "no_threat",
                "confidence": max_confidence,
                "severity": severity,
                "threat_detected": threat_detected,
                "num_detections": len(fused_boxes),
                "bounding_boxes": bounding_boxes,
                "image_size": {
                    "width": img_w,
                    "height": img_h
                }
            }

            if camera_id:
                response["camera_id"] = camera_id

            logger.info(
                f"Detection complete: {dominant_class} "
                f"(conf={max_confidence:.2f}, severity={severity})"
            )

            return response

        except Exception as e:
            logger.error(f"Detection error: {str(e)}", exc_info=True)
            raise

    def detect_from_path(
        self,
        image_path: str,
        **kwargs
    ) -> Dict:
        """
        Run detection on an image file

        Args:
            image_path: Path to image file
            **kwargs: Additional arguments for detect()

        Returns:
            Detection results
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image from {image_path}")

        return self.detect(image, **kwargs)

    def health_check(self) -> Dict:
        """
        Check if all models are loaded and ready

        Returns:
            Health status dictionary
        """
        return {
            "status": "healthy",
            "models_loaded": len(self.models),
            "model_names": self.model_names,
            "device": self.device,
            "cuda_available": torch.cuda.is_available()
        }
