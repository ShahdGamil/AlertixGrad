"""
Configuration for YOLOv8 Ensemble AI Inference Service
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Service Configuration
    APP_NAME: str = "InstaGuard AI Detection Service"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 5001

    # Security
    API_KEY: str = "your-secret-api-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5000", "http://localhost:3000"]

    # Model Paths (relative to project root)
    MODEL_YOLOV8N_PATH: str = "../backend/models/yolov8n/weights/best.pt"
    MODEL_YOLOV8S_PATH: str = "../backend/models/yolov8s/weights/best.pt"
    MODEL_YOLOV8M_PATH: str = "../backend/models/yolov8m/weights/best.pt"

    # Ensemble Configuration (matching notebook validated values)
    ENSEMBLE_IOU_THRESHOLD: float = 0.55  # WBF iou_thr from notebook
    ENSEMBLE_SKIP_BOX_THRESHOLD: float = 0.25  # WBF skip_box_thr from notebook
    ENSEMBLE_WEIGHTS: List[float] = [1.0, 0.3, 1.0]  # n, s, m - YOLOv8s downweighted due to poor performance

    # Detection Configuration
    CONFIDENCE_THRESHOLD: float = 0.25
    IOU_THRESHOLD: float = 0.45
    MAX_DETECTIONS: int = 100

    # Image Processing
    IMAGE_SIZE: int = 640
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/jpg", "image/png"]

    # Video/Stream Processing
    FRAME_SKIP: int = 5  # Process every Nth frame for streams
    MAX_STREAM_DURATION: int = 300  # 5 minutes max

    # Performance
    DEVICE: str = "cuda"  # "cuda" or "cpu"
    BATCH_SIZE: int = 1
    NUM_WORKERS: int = 4

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Class names for theft detection (6 classes matching notebook)
CLASS_NAMES = {
    0: "customer_bagpack",
    1: "product",
    2: "product_picked",
    3: "shopping_cart",
    4: "normal",
    5: "theft"
}


# Severity mapping based on confidence (6-class system)
def get_severity(confidence: float, detection_class: str) -> str:
    """Determine severity based on confidence and class"""
    threat_classes = ["theft", "product_picked", "customer_bagpack"]
    suspicious_classes = ["shopping_cart"]

    if detection_class == "theft":
        if confidence >= 0.85:
            return "critical"
        elif confidence >= 0.70:
            return "high"
        else:
            return "medium"
    elif detection_class in ["product_picked", "customer_bagpack"]:
        if confidence >= 0.75:
            return "high"
        else:
            return "medium"
    elif detection_class in suspicious_classes:
        return "medium" if confidence >= 0.60 else "low"
    else:
        return "low"
