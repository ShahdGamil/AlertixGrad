"""
InstaGuard AI Detection Service - Main FastAPI Application
Production-grade YOLOv8 Ensemble inference service
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
import cv2
import numpy as np
from datetime import datetime
import uvicorn
import io
from PIL import Image

from .config import settings
from .ensemble_model import YOLOv8Ensemble
from .stream_processor import StreamProcessor

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade YOLOv8 Ensemble theft detection service",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance (loaded on startup)
ensemble_model: Optional[YOLOv8Ensemble] = None
stream_processor: Optional[StreamProcessor] = None


# --- Pydantic Models ---

class DetectionRequest(BaseModel):
    """Request model for detection"""
    camera_id: Optional[str] = Field(None, description="Camera identifier")
    conf_threshold: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence threshold (0.0-1.0)"
    )
    iou_threshold: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="IOU threshold for NMS (0.0-1.0)"
    )


class StreamRequest(BaseModel):
    """Request model for stream processing"""
    stream_url: str = Field(..., description="RTSP or HTTP stream URL")
    camera_id: str = Field(..., description="Camera identifier")
    duration: Optional[int] = Field(
        60,
        ge=1,
        le=settings.MAX_STREAM_DURATION,
        description="Processing duration in seconds"
    )
    frame_skip: Optional[int] = Field(
        settings.FRAME_SKIP,
        ge=1,
        le=30,
        description="Process every Nth frame"
    )


class BoundingBox(BaseModel):
    """Bounding box model"""
    label: str
    confidence: float
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    width: int
    height: int


class DetectionResponse(BaseModel):
    """Response model for detection"""
    event: str
    confidence: float
    severity: str
    threat_detected: bool
    num_detections: int
    bounding_boxes: List[BoundingBox]
    camera_id: Optional[str] = None
    timestamp: str
    image_size: dict
    processing_time_ms: Optional[float] = None


# --- Security ---

async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from header"""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


# --- Startup/Shutdown Events ---

@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    global ensemble_model, stream_processor

    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)

    try:
        # Initialize ensemble model
        logger.info("Loading YOLOv8 Ensemble models...")
        ensemble_model = YOLOv8Ensemble()
        logger.info("✓ Ensemble models loaded successfully")

        # Initialize stream processor
        logger.info("Initializing stream processor...")
        stream_processor = StreamProcessor(ensemble_model)
        logger.info("✓ Stream processor initialized")

        logger.info("=" * 60)
        logger.info("🚀 AI Service ready for inference!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Failed to initialize models: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI service...")
    if stream_processor:
        stream_processor.cleanup()
    logger.info("✓ Shutdown complete")


# --- Health & Monitoring Endpoints ---

@app.get("/health")
async def health_check():
    """Basic health check endpoint (no auth required)"""
    if ensemble_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")

    health_status = ensemble_model.health_check()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        **health_status
    }


@app.get(f"{settings.API_PREFIX}/status", dependencies=[Depends(verify_api_key)])
async def detailed_status():
    """Detailed status endpoint (requires auth)"""
    if ensemble_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")

    health_status = ensemble_model.health_check()
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "models": health_status,
        "config": {
            "device": settings.DEVICE,
            "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
            "iou_threshold": settings.IOU_THRESHOLD,
            "ensemble_weights": settings.ENSEMBLE_WEIGHTS,
            "image_size": settings.IMAGE_SIZE
        }
    }


# --- Detection Endpoints ---

@app.post(
    f"{settings.API_PREFIX}/detect/image",
    response_model=DetectionResponse,
    dependencies=[Depends(verify_api_key)]
)
async def detect_from_image(
    image: UploadFile = File(...),
    camera_id: Optional[str] = None,
    conf_threshold: Optional[float] = None,
    iou_threshold: Optional[float] = None
):
    """
    Detect threats in a single image

    Args:
        image: Image file (JPEG, PNG)
        camera_id: Optional camera identifier
        conf_threshold: Optional confidence threshold override
        iou_threshold: Optional IOU threshold override

    Returns:
        Detection results with bounding boxes
    """
    if ensemble_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")

    start_time = datetime.utcnow()

    try:
        # Validate file type
        if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Allowed: {settings.ALLOWED_IMAGE_TYPES}"
            )

        # Read image file
        contents = await image.read()
        if len(contents) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Image too large. Max size: {settings.MAX_IMAGE_SIZE_MB}MB"
            )

        # Convert to numpy array
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Failed to decode image")

        # Run detection
        result = ensemble_model.detect(
            img,
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold,
            camera_id=camera_id
        )

        # Add timestamp and processing time
        end_time = datetime.utcnow()
        result["timestamp"] = end_time.isoformat() + "Z"
        result["processing_time_ms"] = (end_time - start_time).total_seconds() * 1000

        logger.info(
            f"Detection request processed: "
            f"camera={camera_id}, event={result['event']}, "
            f"time={result['processing_time_ms']:.2f}ms"
        )

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.post(
    f"{settings.API_PREFIX}/detect/batch",
    dependencies=[Depends(verify_api_key)]
)
async def detect_batch(
    images: List[UploadFile] = File(...),
    camera_id: Optional[str] = None
):
    """
    Batch detection on multiple images

    Args:
        images: List of image files
        camera_id: Optional camera identifier

    Returns:
        List of detection results
    """
    if ensemble_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")

    if len(images) > 10:
        raise HTTPException(status_code=400, detail="Max 10 images per batch")

    results = []
    for idx, image in enumerate(images):
        try:
            # Read and process image
            contents = await image.read()
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                results.append({
                    "success": False,
                    "error": "Failed to decode image",
                    "filename": image.filename
                })
                continue

            # Run detection
            result = ensemble_model.detect(img, camera_id=camera_id)
            result["success"] = True
            result["filename"] = image.filename
            result["timestamp"] = datetime.utcnow().isoformat() + "Z"
            results.append(result)

        except Exception as e:
            logger.error(f"Batch detection error for {image.filename}: {str(e)}")
            results.append({
                "success": False,
                "error": str(e),
                "filename": image.filename
            })

    return JSONResponse(content={"results": results, "total": len(images)})


@app.post(
    f"{settings.API_PREFIX}/detect/stream",
    dependencies=[Depends(verify_api_key)]
)
async def detect_from_stream(request: StreamRequest):
    """
    Process RTSP/HTTP video stream

    Args:
        request: Stream request with URL, camera ID, and parameters

    Returns:
        Stream processing task ID (for async processing)
    """
    if stream_processor is None:
        raise HTTPException(status_code=503, detail="Stream processor not initialized")

    try:
        task_id = await stream_processor.process_stream(
            stream_url=request.stream_url,
            camera_id=request.camera_id,
            duration=request.duration,
            frame_skip=request.frame_skip
        )

        return {
            "task_id": task_id,
            "camera_id": request.camera_id,
            "stream_url": request.stream_url,
            "status": "processing",
            "message": "Stream processing started"
        }

    except Exception as e:
        logger.error(f"Stream processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stream processing failed: {str(e)}")


# --- Root Endpoint ---

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": f"{settings.API_PREFIX}/docs"
    }


# --- Run Server ---

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level=settings.LOG_LEVEL.lower()
    )
