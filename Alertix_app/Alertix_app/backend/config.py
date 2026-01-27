"""
Configuration file for Alertix YOLO Theft Detection API
========================================================
Modify these settings without touching the main backend code.
"""

import os

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Path to your YOLO model file
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "best (5).pt"  # Using your uploaded model
)

# Alternative: Use absolute path
# MODEL_PATH = "/path/to/your/model.pt"

# Confidence threshold for detections (0.0 to 1.0)
CONFIDENCE_THRESHOLD = 0.25

# IoU threshold for Non-Maximum Suppression (0.0 to 1.0)
IOU_THRESHOLD = 0.45

# Device to run inference on
# Options: 'cpu', 'cuda', 'mps' (Mac M1/M2)
DEVICE = 'cpu'  # Use 'cpu' for Raspberry Pi

# ============================================================================
# CLASS CONFIGURATION
# ============================================================================

# Class names mapping
# Modify this based on your model's classes
CLASS_NAMES = {
    0: "Theft",
    1: "Normal",
    2: "Product"  # Add more classes if needed
}

# Colors for bounding boxes (BGR format for OpenCV)
# Format: (Blue, Green, Red)
CLASS_COLORS = {
    0: (0, 0, 255),    # Red for Theft
    1: (0, 255, 0),    # Green for Normal
    2: (255, 0, 0)     # Blue for Product
}

# Theft class ID (class that triggers theft detection)
THEFT_CLASS_ID = 0

# ============================================================================
# SERVER CONFIGURATION
# ============================================================================

# Server host (0.0.0.0 allows external connections)
HOST = "0.0.0.0"

# Server port
PORT = 8003

# Enable auto-reload (set to False in production)
RELOAD = True

# Number of worker processes (1 is recommended for Raspberry Pi)
WORKERS = 1

# Maximum upload file size (in bytes)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

# Allowed origins for CORS
# In production, specify your Flutter app domains
ALLOWED_ORIGINS = [
    "*",  # Allow all origins (development only)
    # "http://localhost:3000",  # Flutter web local
    # "https://yourapp.com",     # Production domain
]

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ============================================================================
# IMAGE PROCESSING CONFIGURATION
# ============================================================================

# Image quality for base64 encoding (1-100)
JPEG_QUALITY = 85

# Font scale for labels on bounding boxes
LABEL_FONT_SCALE = 0.6

# Line thickness for bounding boxes
BOX_LINE_THICKNESS = 2

# Text thickness for labels
TEXT_THICKNESS = 2

# ============================================================================
# RASPBERRY PI OPTIMIZATIONS
# ============================================================================

# Enable model warmup on startup (improves first inference speed)
WARMUP_MODEL = True

# Warmup image size (width, height)
WARMUP_IMAGE_SIZE = (640, 640)

# Maximum image dimensions for inference (resize if larger)
# Set to None to disable resizing
MAX_IMAGE_WIDTH = 1920
MAX_IMAGE_HEIGHT = 1920

# ============================================================================
# RESPONSE CONFIGURATION
# ============================================================================

# Include base64 image in response by default
DEFAULT_INCLUDE_IMAGE = True

# Calculate overall confidence in response
INCLUDE_OVERALL_CONFIDENCE = True

# Include detection statistics in response
INCLUDE_STATISTICS = True

# ============================================================================
# EMAIL NOTIFICATION CONFIGURATION (Gmail SMTP)
# ============================================================================

# Gmail SMTP settings
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Your Gmail address
EMAIL_ADDRESS = "judyahmedmahmoud261@gmail.com"

# IMPORTANT: Use Gmail App Password (NOT your regular password)
# To generate: Google Account > Security > 2-Step Verification > App Passwords
EMAIL_APP_PASSWORD = "iauvjuwstpembvge"  # Gmail App Password

# Email to receive alerts (can be same as EMAIL_ADDRESS)
RECEIVER_EMAIL = "judyahmedmahmoud261@gmail.com"

# Enable email notifications (set to False to disable)
EMAIL_NOTIFICATIONS_ENABLED = True

# Email retry attempts on failure
EMAIL_RETRY_ATTEMPTS = 1

# ============================================================================
# AUTHENTICATION CONFIGURATION (JWT)
# ============================================================================

# Secret key for JWT token signing (CHANGE THIS IN PRODUCTION!)
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY = "alertix-theft-detection-secret-key-change-in-production-2026"

# JWT token expiration time (in hours)
JWT_ACCESS_TOKEN_EXPIRE_HOURS = 24

# JWT algorithm
JWT_ALGORITHM = "HS256"

# Password hashing settings
PASSWORD_MIN_LENGTH = 6
