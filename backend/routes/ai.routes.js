import express from 'express';
import multer from 'multer';
import path from 'path';
import {
  processImage,
  analyzeUploadedImage,
  startCameraStream,
  receiveDetectionWebhook,
  getAIStatus,
  getStreamStatus,
  stopCameraStream
} from '../controllers/ai.controller.js';
import { authenticate, authorize } from '../middleware/auth.middleware.js';
import { auditLog } from '../middleware/audit.middleware.js';

const router = express.Router();

// Configure multer for image uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/snapshots/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    // Only allow image files
    const allowedTypes = /jpeg|jpg|png/;
    const mimetype = allowedTypes.test(file.mimetype);
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());

    if (mimetype && extname) {
      return cb(null, true);
    }

    cb(new Error('Only .jpg, .jpeg, and .png files are allowed'));
  }
});

// ========== Public Endpoints ==========

/**
 * Webhook endpoint for AI service to send detections
 * No authentication - AI service will validate using its own mechanism
 */
router.post('/webhook/detection', receiveDetectionWebhook);

// ========== Authenticated Endpoints ==========

// All routes below require authentication
router.use(authenticate);

/**
 * Analyze uploaded image for theft detection (manual upload - no camera required)
 * POST /api/v1/ai/analyze
 * Body: multipart/form-data with 'image' field
 * Used for testing AI detection without a camera
 * Requires: admin or operator role
 */
router.post(
  '/analyze',
  authorize('admin', 'operator'),
  upload.single('image'),
  analyzeUploadedImage
);

/**
 * Process image through AI detection
 * POST /api/v1/ai/detect/:cameraId
 * Body: multipart/form-data with 'image' field
 * Requires: admin or operator role
 */
router.post(
  '/detect/:cameraId',
  authorize('admin', 'operator'),
  upload.single('image'),
  auditLog('ai_detect_image', 'Camera'),
  processImage
);

/**
 * Start real-time stream monitoring
 * POST /api/v1/ai/stream/start/:cameraId
 * Body: { duration?: number, frame_skip?: number }
 * Requires: admin or operator role
 */
router.post(
  '/stream/start/:cameraId',
  authorize('admin', 'operator'),
  auditLog('ai_stream_start', 'Camera'),
  startCameraStream
);

/**
 * Get stream processing status
 * GET /api/v1/ai/stream/status/:taskId
 * Requires: any authenticated user
 */
router.get(
  '/stream/status/:taskId',
  getStreamStatus
);

/**
 * Stop stream processing
 * POST /api/v1/ai/stream/stop/:taskId
 * Requires: admin or operator role
 */
router.post(
  '/stream/stop/:taskId',
  authorize('admin', 'operator'),
  auditLog('ai_stream_stop', 'Stream'),
  stopCameraStream
);

/**
 * Get AI service status
 * GET /api/v1/ai/status
 * Requires: any authenticated user
 */
router.get('/status', getAIStatus);

export default router;
