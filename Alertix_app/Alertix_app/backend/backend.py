"""
FastAPI Backend for YOLO Theft Detection System
================================================
This backend provides REST API endpoints for the Alertix Flutter app.
It loads a YOLO model ONCE at startup and performs real-time theft detection
on uploaded images from the mobile app.

Configuration matches the training notebook exactly:
- 6 Classes: Customer-Bagpack, Product, Product-Picked, Shopping-Cart, normal, theft
- Class 4 = normal, Class 5 = theft
- IMG_SIZE = 640
- CONF_THRESHOLD = 0.25
- IOU_THRESHOLD = 0.5

Author: Alertix Team
Date: 2026-01-25

Usage:
    uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
"""

# ============================================================================
# IMPORTS
# ============================================================================

import os
import io
import base64
import logging
from typing import List, Dict, Any
from datetime import datetime

import cv2
import numpy as np
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from ultralytics import YOLO

# Database integration
from database import get_db, DatabaseManager

# Email notification service
from email_service import send_theft_alert_email

# Authentication service
from auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    get_user_from_token,
    generate_user_id,
    validate_password
)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION - MATCHING NOTEBOOK EXACTLY
# ============================================================================

# Model configuration - Single model (using absolute path)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "best (4).pt")

# YOLO inference settings - MATCHING NOTEBOOK EXACTLY
IMG_SIZE = 640              # Match training resolution
CONF_THRESHOLD = 0.25       # From notebook
IOU_THRESHOLD = 0.5         # From notebook (was 0.45, notebook uses 0.5)

# Device selection (GPU if available, otherwise CPU)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ============================================================================
# CLASS MAPPING - EXACTLY FROM NOTEBOOK
# ============================================================================
# From notebook: 'names': ['Customer-Bagpack', 'Product', 'Product-Picked', 'Shopping-Cart', 'normal', 'theft']

CLASS_NAMES = {
    0: "Customer-Bagpack",
    1: "Product",
    2: "Product-Picked",
    3: "Shopping-Cart",
    4: "normal",
    5: "theft"
}

# Class IDs - EXACTLY FROM NOTEBOOK
THEFT_CLASS_ID = 5      # theft is class 5
NORMAL_CLASS_ID = 4     # normal is class 4

# Colors for bounding boxes (BGR format for OpenCV)
COLORS = {
    0: (255, 165, 0),   # Orange - Customer-Bagpack
    1: (255, 0, 0),     # Blue - Product
    2: (255, 0, 255),   # Magenta - Product-Picked
    3: (0, 255, 255),   # Yellow - Shopping-Cart
    4: (0, 255, 0),     # Green - normal
    5: (0, 0, 255)      # Red - theft
}

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Alertix YOLO Theft Detection API",
    description="REST API for real-time theft detection using YOLO model. Compatible with Flutter frontend.",
    version="1.0.0"
)

# Enable CORS for Flutter web and mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# GLOBAL MODEL INSTANCE
# ============================================================================

# Model is loaded ONCE at startup - NOT inside endpoints
model: YOLO = None
model_loaded: bool = False

# ============================================================================
# MODEL LOADING (CALLED ONCE AT STARTUP)
# ============================================================================

def load_model():
    """
    Load YOLO model ONCE at server startup.
    Verifies class names match the notebook configuration.
    """
    global model, model_loaded

    try:
        # Step 1: Verify model file exists
        logger.info(f"Model path: {MODEL_PATH}")

        if not os.path.exists(MODEL_PATH):
            logger.error(f"Model file not found: {MODEL_PATH}")
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

        logger.info(f"Model file verified: {MODEL_PATH}")

        # Step 2: Load YOLO model
        logger.info("Loading YOLO model...")
        model = YOLO(MODEL_PATH)

        # Step 3: Move model to GPU if available
        logger.info(f"Using device: {DEVICE}")
        if DEVICE == "cuda":
            model.to("cuda")
            logger.info("Model moved to GPU (CUDA)")

        # Step 4: Log model's class names and verify they match
        if hasattr(model, 'names') and model.names:
            logger.info(f"Model class names: {model.names}")

            # Verify the model has our expected classes
            model_classes = model.names
            for cls_id, cls_name in model_classes.items():
                expected = CLASS_NAMES.get(cls_id, "Unknown")
                if cls_name.lower() != expected.lower():
                    logger.warning(f"Class mismatch at ID {cls_id}: model has '{cls_name}', expected '{expected}'")
                else:
                    logger.info(f"  Class {cls_id}: {cls_name} ✓")
        else:
            logger.warning("Could not read class names from model!")

        # Step 5: Warm up model with dummy image
        logger.info("Warming up model...")
        dummy_image = np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
        _ = model.predict(
            dummy_image,
            imgsz=IMG_SIZE,
            conf=CONF_THRESHOLD,
            iou=IOU_THRESHOLD,
            verbose=False
        )

        model_loaded = True
        logger.info("=" * 50)
        logger.info("Model loaded and warmed up successfully!")
        logger.info(f"  - Theft class ID: {THEFT_CLASS_ID}")
        logger.info(f"  - Normal class ID: {NORMAL_CLASS_ID}")
        logger.info(f"  - Confidence threshold: {CONF_THRESHOLD}")
        logger.info(f"  - IOU threshold: {IOU_THRESHOLD}")
        logger.info("=" * 50)
        return True

    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        model_loaded = False
        raise e

# ============================================================================
# STARTUP EVENT - LOADS MODEL ONCE
# ============================================================================

@app.on_event("startup")
def startup_event():
    """FastAPI startup event - loads model and initializes database."""
    logger.info("=" * 70)
    logger.info("Starting Alertix YOLO Theft Detection API Server")
    logger.info("=" * 70)

    # Load YOLO model
    load_model()

    # Initialize database
    db = get_db()
    alert_count = db.get_alert_count()
    logger.info(f"✓ Database initialized - {alert_count} stored alerts")

    logger.info("Server ready to accept requests!")
    logger.info("=" * 70)

# ============================================================================
# IMAGE PROCESSING FUNCTIONS
# ============================================================================

def decode_image(file_bytes: bytes) -> np.ndarray:
    """
    Decode uploaded image bytes into OpenCV format using cv2.imdecode.
    Does NOT pass raw bytes directly to YOLO.
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(file_bytes, np.uint8)

        # Decode image using OpenCV
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode image")

        logger.info(f"Image decoded: {image.shape}")
        return image

    except Exception as e:
        logger.error(f"Error decoding image: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


def draw_bounding_boxes(image: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
    """Draw bounding boxes and labels on the image using OpenCV."""
    output_image = image.copy()

    for detection in detections:
        bbox = detection["bbox"]
        confidence = detection["confidence"]
        class_name = detection["class"]
        class_id = detection.get("class_id", 0)

        # Get coordinates
        x1, y1, x2, y2 = map(int, bbox)

        # Get color based on class ID
        color = COLORS.get(class_id, (255, 255, 255))

        # Draw rectangle (thicker for theft)
        thickness = 3 if class_id == THEFT_CLASS_ID else 2
        cv2.rectangle(output_image, (x1, y1), (x2, y2), color, thickness)

        # Prepare label text
        label = f"{class_name}: {confidence:.2f}"

        # Get text size for background rectangle
        (text_width, text_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )

        # Draw background rectangle for text
        cv2.rectangle(
            output_image,
            (x1, y1 - text_height - baseline - 5),
            (x1 + text_width, y1),
            color,
            -1
        )

        # Draw text
        cv2.putText(
            output_image,
            label,
            (x1, y1 - baseline - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

    return output_image


def encode_image_to_base64(image: np.ndarray) -> str:
    """Encode OpenCV image to Base64 string for Flutter."""
    try:
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        img_str = base64.b64encode(buffer).decode('utf-8')
        return img_str
    except Exception as e:
        logger.error(f"Error encoding image to base64: {str(e)}")
        return ""

# ============================================================================
# YOLO INFERENCE FUNCTION
# ============================================================================

def run_inference(image: np.ndarray) -> List[Dict[str, Any]]:
    """
    Run YOLO inference on the decoded image.

    Uses settings matching the notebook:
    - imgsz = 640
    - conf = 0.25
    - iou = 0.5
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Run YOLO inference with EXACT notebook settings
        results = model.predict(
            image,
            imgsz=IMG_SIZE,
            conf=CONF_THRESHOLD,
            iou=IOU_THRESHOLD,
            verbose=False,
            device=DEVICE
        )

        detections = []

        # Process results using correct YOLO output indexing
        if len(results) > 0:
            result = results[0]

            if result.boxes is not None and len(result.boxes) > 0:
                # Extract xyxy bounding boxes
                boxes = result.boxes.xyxy.cpu().numpy()
                # Extract confidence scores
                confidences = result.boxes.conf.cpu().numpy()
                # Extract class IDs
                classes = result.boxes.cls.cpu().numpy().astype(int)

                for box, conf, cls_id in zip(boxes, confidences, classes):
                    # Get class name from our mapping
                    cls_name = CLASS_NAMES.get(int(cls_id), f"Class_{cls_id}")

                    detection = {
                        "class": cls_name,
                        "confidence": float(conf),
                        "bbox": [float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                        "class_id": int(cls_id)
                    }
                    detections.append(detection)

                    # Log each detection
                    logger.info(f"  Detected: {cls_name} (class {cls_id}) conf: {conf:.3f}")

        # Sort by confidence (highest first)
        detections.sort(key=lambda x: x["confidence"], reverse=True)

        # Log detection count
        logger.info(f"Total detections: {len(detections)}")

        return detections

    except Exception as e:
        logger.error(f"Error during inference: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

# ============================================================================
# DETECTION LOGIC - MATCHING NOTEBOOK
# ============================================================================

def analyze_detections(detections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze detections and determine prediction result.

    Logic:
    - If ANY detection has class_id = 5 (theft) -> prediction = "Theft", alert = True
    - Otherwise -> prediction = "Normal", alert = False
    """
    theft_detected = False
    highest_confidence = 0.0
    theft_confidence = 0.0

    # Check if ANY detection is Theft (class_id = 5)
    for detection in detections:
        conf = detection["confidence"]
        cls_id = detection.get("class_id", -1)

        # Update highest confidence
        if conf > highest_confidence:
            highest_confidence = conf

        # Check for theft (class_id = 5)
        if cls_id == THEFT_CLASS_ID:
            theft_detected = True
            if conf > theft_confidence:
                theft_confidence = conf
            logger.info(f">>> THEFT DETECTED! Confidence: {conf:.3f}")

    # Determine prediction based on theft detection
    if theft_detected:
        prediction = "Theft"
        message = "Suspicious behavior detected"
        alert = True
        confidence = theft_confidence
    else:
        prediction = "Normal"
        message = "Normal activity"
        alert = False
        confidence = highest_confidence

    # Log prediction result
    logger.info(f"Final Prediction: {prediction}")
    logger.info(f"Confidence: {confidence:.3f}")
    logger.info(f"Alert: {alert}")

    return {
        "prediction": prediction,
        "confidence": confidence,
        "alert": alert,
        "message": message
    }

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "Server running",
            "model_loaded": model_loaded,
            "device": DEVICE,
            "model_file": os.path.basename(MODEL_PATH),
            "class_mapping": CLASS_NAMES,
            "theft_class_id": THEFT_CLASS_ID,
            "normal_class_id": NORMAL_CLASS_ID,
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/register")
def register_user(request: RegisterRequest):
    """
    Register a new user account.

    Required fields:
    - full_name: Full name
    - email: Email address (unique)
    - password: Password (min 6 characters)

    Returns:
        User profile and JWT access token
    """
    try:
        # Validate password
        is_valid, error_msg = validate_password(request.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Validate email format
        if "@" not in request.email or "." not in request.email:
            raise HTTPException(status_code=400, detail="Invalid email format")

        # Check if email already exists
        db = get_db()
        existing_user = db.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=409, detail="Email already registered")

        # Create user
        user_id = generate_user_id()
        password_hash = hash_password(request.password)

        user = db.create_user(
            user_id=user_id,
            full_name=request.full_name,
            email=request.email,
            password_hash=password_hash
        )

        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user")

        # Generate access token
        token = create_access_token(
            user_id=user_id,
            email=request.email,
            full_name=request.full_name
        )

        logger.info(f"✅ New user registered: {request.email}")

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "User registered successfully",
                "user": {
                    "user_id": user["user_id"],
                    "full_name": user["full_name"],
                    "email": user["email"],
                    "created_at": user["created_at"]
                },
                "access_token": token,
                "token_type": "bearer"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/login")
def login_user(request: LoginRequest):
    """
    Login with email and password.

    Returns:
        User profile and JWT access token
    """
    try:
        db = get_db()

        # Find user by email
        user = db.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password
        if not verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(status_code=403, detail="Account is disabled")

        # Update last login
        db.update_last_login(user["user_id"])

        # Generate access token
        token = create_access_token(
            user_id=user["user_id"],
            email=user["email"],
            full_name=user["full_name"]
        )

        logger.info(f"✅ User logged in: {request.email}")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Login successful",
                "user": {
                    "user_id": user["user_id"],
                    "full_name": user["full_name"],
                    "email": user["email"],
                    "created_at": user["created_at"],
                    "last_login": datetime.now().isoformat()
                },
                "access_token": token,
                "token_type": "bearer"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/me")
def get_current_user(authorization: str = None):
    """
    Get current user profile from JWT token.

    Requires Authorization header: Bearer <token>
    """
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")

        # Extract token from "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization format")

        token = parts[1]

        # Verify token
        user_info = get_user_from_token(token)
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Get full user data from database
        db = get_db()
        user = db.get_user_by_id(user_info["user_id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "user": {
                    "user_id": user["user_id"],
                    "full_name": user["full_name"],
                    "email": user["email"],
                    "created_at": user["created_at"],
                    "last_login": user.get("last_login")
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/logout")
def logout_user():
    """
    Logout current user.

    Note: JWT tokens are stateless, so this is mostly for client-side cleanup.
    The client should delete the stored token.
    """
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Logged out successfully. Please delete your access token."
        }
    )


# ============================================================================
# PREDICTION ENDPOINT
# ============================================================================

@app.post("/predict")
def predict_theft(
    image: UploadFile = File(...),
    include_image: bool = Form(True),
    camera_id: str = Form("unknown"),
    camera_name: str = Form(None)
):
    """
    Main prediction endpoint for theft detection.

    Automatically saves theft alerts to database when detected.

    Returns Flutter-friendly JSON:
    {
        "prediction": "Theft" or "Normal",
        "confidence": float,
        "alert": true/false,
        "message": "Suspicious behavior detected" or "Normal activity",
        "detections": [...],
        "image_with_boxes": "base64string",
        "alert_id": int (if theft detected and saved)
    }
    """
    try:
        logger.info("=" * 50)
        logger.info("Received prediction request")

        # Step 1: Read image file
        image_bytes = image.file.read()

        # Validate image size (10MB limit)
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image file too large (max 10MB)")

        # Step 2: Decode image using cv2.imdecode
        image_cv = decode_image(image_bytes)

        # Step 3: Run YOLO inference
        detections = run_inference(image_cv)

        # Step 4: Analyze detections (theft detection logic)
        analysis = analyze_detections(detections)

        # Step 5: Prepare Flutter-friendly response
        response_data = {
            "prediction": analysis["prediction"],
            "confidence": round(analysis["confidence"], 4),
            "alert": analysis["alert"],
            "message": analysis["message"],
            "detections": [
                {
                    "class": d["class"],
                    "confidence": round(d["confidence"], 4),
                    "bbox": [round(x, 2) for x in d["bbox"]]
                }
                for d in detections
            ],
            "detection_count": len(detections),
            "timestamp": datetime.now().isoformat()
        }

        # Step 6: Draw bounding boxes and encode to base64
        base64_image = None
        if include_image:
            if len(detections) > 0:
                image_with_boxes = draw_bounding_boxes(image_cv, detections)
            else:
                image_with_boxes = image_cv

            base64_image = encode_image_to_base64(image_with_boxes)
            response_data["image_with_boxes"] = base64_image

        # Step 7: Auto-save alert to database if theft detected
        if analysis["alert"]:
            try:
                db = get_db()

                # Prepare bbox data for database
                bbox_data = [
                    {
                        "class": d["class"],
                        "confidence": d["confidence"],
                        "bbox": d["bbox"]
                    }
                    for d in detections
                ]

                # Save alert to database
                alert_id = db.save_alert(
                    camera_id=camera_id,
                    camera_name=camera_name,
                    timestamp=response_data["timestamp"],
                    theft_detected=True,
                    confidence_score=analysis["confidence"],
                    detected_class="theft",
                    description=analysis["message"],
                    bbox_data=bbox_data,
                    image_base64=base64_image  # Save image if available
                )

                response_data["alert_id"] = alert_id
                logger.info(f"✓ Alert saved to database with ID: {alert_id}")

                # Update camera state
                db.update_camera_state(
                    camera_id=camera_id,
                    camera_name=camera_name,
                    last_detection_status="theft",
                    last_image_snapshot=base64_image[:100] if base64_image else None  # Store small preview
                )

                # Step 8: Send email notification (non-blocking)
                try:
                    email_sent = send_theft_alert_email(
                        camera_name=camera_name or f"Camera {camera_id[:8]}",
                        camera_id=camera_id,
                        confidence=analysis["confidence"],
                        timestamp=response_data["timestamp"],
                        image_base64=base64_image,
                        detections=detections
                    )
                    if email_sent:
                        logger.info("✅ Email notification sent")
                        response_data["email_sent"] = True
                    else:
                        logger.warning("⚠️ Email notification not sent (check config)")
                        response_data["email_sent"] = False
                except Exception as email_err:
                    logger.error(f"Email error (non-blocking): {email_err}")
                    response_data["email_sent"] = False

            except Exception as e:
                logger.error(f"Failed to save alert to database: {e}")
                # Continue anyway - don't fail the request

        logger.info(f"Response: prediction={analysis['prediction']}, alert={analysis['alert']}")
        logger.info("=" * 50)

        return JSONResponse(status_code=200, content=response_data)

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in prediction endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# ALERT MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/alerts")
def get_all_alerts(limit: int = None):
    """
    Get all stored alerts, sorted by newest first.

    Query Parameters:
    - limit (optional): Maximum number of alerts to return

    Returns:
        List of alert objects with all metadata
    """
    try:
        db = get_db()
        alerts = db.get_all_alerts(limit=limit)

        logger.info(f"Retrieved {len(alerts)} alerts")

        return JSONResponse(
            status_code=200,
            content={
                "alerts": alerts,
                "total_count": len(alerts),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts/{alert_id}")
def get_alert_by_id(alert_id: int):
    """
    Get a single alert by ID.

    Returns:
        Full alert data including image and bounding boxes
    """
    try:
        db = get_db()
        alert = db.get_alert_by_id(alert_id)

        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

        return JSONResponse(status_code=200, content=alert)

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving alert {alert_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/alerts/{alert_id}/read")
def mark_alert_as_viewed(alert_id: int):
    """
    Mark an alert as viewed/read.

    Returns:
        Success status
    """
    try:
        db = get_db()
        updated = db.mark_alert_as_viewed(alert_id)

        if not updated:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "alert_id": alert_id,
                "message": f"Alert {alert_id} marked as viewed"
            }
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error marking alert {alert_id} as viewed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/alerts/clear")
def clear_all_alerts():
    """
    Delete all alerts from the database.

    Returns:
        Number of alerts deleted
    """
    try:
        db = get_db()
        deleted_count = db.clear_all_alerts()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Cleared {deleted_count} alerts"
            }
        )

    except Exception as e:
        logger.error(f"Error clearing alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cameras")
def get_all_cameras(user_id: str = None):
    """
    Get all cameras and their configurations.

    Args:
        user_id: Optional filter by user ID

    Returns:
        List of camera objects with metadata
    """
    try:
        db = get_db()
        cameras = db.get_all_cameras(user_id=user_id)

        return JSONResponse(
            status_code=200,
            content={
                "cameras": cameras,
                "total_count": len(cameras),
                "timestamp": datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving cameras: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cameras")
def create_camera(
    camera_id: str = Form(...),
    camera_name: str = Form(...),
    location: str = Form(None),
    camera_number: str = Form(None),
    is_active: bool = Form(True),
    created_at: str = Form(None),
    user_id: str = Form("default_user"),
):
    """
    Create or update a camera configuration.

    Returns:
        The saved camera object
    """
    try:
        db = get_db()

        saved_id = db.save_camera(
            camera_id=camera_id,
            camera_name=camera_name,
            location=location,
            camera_number=camera_number,
            is_active=is_active,
            created_at=created_at,
            user_id=user_id
        )

        # Fetch the saved camera to return
        camera = db.get_camera_by_id(saved_id)

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "camera": camera,
                "message": f"Camera '{camera_name}' saved successfully"
            }
        )

    except Exception as e:
        logger.error(f"Error saving camera: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cameras/{camera_id}")
def get_camera(camera_id: str):
    """Get a single camera by ID."""
    try:
        db = get_db()
        camera = db.get_camera_by_id(camera_id)

        if not camera:
            raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

        return JSONResponse(status_code=200, content={"camera": camera})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving camera: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/cameras/{camera_id}")
def update_camera(
    camera_id: str,
    camera_name: str = Form(None),
    location: str = Form(None),
    camera_number: str = Form(None),
    is_active: bool = Form(None),
):
    """Update a camera configuration."""
    try:
        db = get_db()

        # Get existing camera
        existing = db.get_camera_by_id(camera_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

        # Update with new values (keep existing if not provided)
        db.save_camera(
            camera_id=camera_id,
            camera_name=camera_name if camera_name is not None else existing['camera_name'],
            location=location if location is not None else existing.get('location'),
            camera_number=camera_number if camera_number is not None else existing.get('camera_number'),
            is_active=is_active if is_active is not None else existing.get('is_active', True),
            created_at=existing.get('created_at'),
            user_id=existing.get('user_id', 'default_user')
        )

        # Fetch updated camera
        camera = db.get_camera_by_id(camera_id)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "camera": camera,
                "message": f"Camera {camera_id} updated"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating camera: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/cameras/clear/all")
def clear_all_cameras(user_id: str = None):
    """Delete all cameras, optionally for a specific user."""
    try:
        db = get_db()
        deleted_count = db.clear_all_cameras(user_id=user_id)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Cleared {deleted_count} cameras"
            }
        )

    except Exception as e:
        logger.error(f"Error clearing cameras: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/cameras/{camera_id}")
def delete_camera(camera_id: str):
    """Delete a camera by ID."""
    try:
        db = get_db()
        deleted = db.delete_camera(camera_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "camera_id": camera_id,
                "message": f"Camera {camera_id} deleted"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting camera: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    """Root endpoint - API information."""
    return {
        "name": "Alertix YOLO Theft Detection API",
        "version": "3.0.0",
        "status": "running",
        "model_loaded": model_loaded,
        "device": DEVICE,
        "class_mapping": CLASS_NAMES,
        "features": [
            "Real-time theft detection",
            "Persistent alert storage (SQLite)",
            "Camera state tracking",
            "Auto-save theft alerts",
            "Email notifications (Gmail SMTP)",
            "User authentication (JWT)"
        ],
        "endpoints": {
            "health": "GET /health",
            "auth_register": "POST /auth/register",
            "auth_login": "POST /auth/login",
            "auth_me": "GET /auth/me",
            "auth_logout": "POST /auth/logout",
            "predict": "POST /predict",
            "get_alerts": "GET /alerts",
            "get_alert": "GET /alerts/{alert_id}",
            "mark_viewed": "PUT /alerts/{alert_id}/read",
            "clear_alerts": "DELETE /alerts/clear",
            "get_cameras": "GET /cameras",
            "create_camera": "POST /cameras",
            "get_camera": "GET /cameras/{camera_id}",
            "update_camera": "PUT /cameras/{camera_id}",
            "delete_camera": "DELETE /cameras/{camera_id}",
            "clear_cameras": "DELETE /cameras/clear/all",
            "docs": "GET /docs"
        }
    }

# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
