import aiServiceClient from '../utils/aiServiceClient.js';
import Alert from '../models/Alert.model.js';
import Snapshot from '../models/Snapshot.model.js';
import Camera from '../models/Camera.model.js';
import Settings from '../models/Settings.model.js';
import fs from 'fs/promises';

/**
 * Analyze uploaded image for theft detection (manual upload - no camera required)
 * This endpoint is used for testing the AI detection system
 */
export const analyzeUploadedImage = async (req, res) => {
  try {
    // Check if file was uploaded
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'No image file provided'
      });
    }

    // Read image buffer
    const imageBuffer = await fs.readFile(req.file.path);

    // Call AI service for detection
    const aiResult = await aiServiceClient.detectImage(imageBuffer, {
      camera_id: 'manual_upload'
    });

    // Transform AI result to simpler format for mobile app
    const detections = aiResult.bounding_boxes.map(box => ({
      class: box.class_name,
      confidence: box.confidence,
      bbox: {
        x: box.x_min,
        y: box.y_min,
        width: box.width,
        height: box.height
      }
    }));

    // Check if theft was detected
    const theftDetected = detections.some(d => d.class === 'theft');

    let snapshot = null;
    let alert = null;

    // If theft detected, save snapshot and create alert
    if (theftDetected) {
      // Save snapshot
      snapshot = await Snapshot.create({
        camera: null, // No camera for manual uploads
        imageUrl: `/uploads/snapshots/${req.file.filename}`,
        thumbnailUrl: `/uploads/snapshots/${req.file.filename}`,
        filename: req.file.filename,
        fileSize: req.file.size,
        mimeType: req.file.mimetype,
        capturedAt: new Date(),
        tags: ['manual_upload', 'theft_detected'],
        metadata: {
          width: aiResult.image_size?.width || 0,
          height: aiResult.image_size?.height || 0,
          aiProcessed: true,
          aiConfidence: aiResult.confidence * 100,
          source: 'manual_upload'
        }
      });

      // Create alert
      alert = await Alert.create({
        camera: null,
        snapshot: snapshot._id,
        type: 'theft',
        severity: aiResult.severity || 'high',
        status: 'open',
        description: `Manual upload: Theft detected with ${(aiResult.confidence * 100).toFixed(1)}% confidence`,
        detectedAt: new Date(),
        metadata: {
          confidence: aiResult.confidence * 100,
          source: 'manual_upload',
          detections: detections
        }
      });
    }

    res.json({
      success: true,
      data: {
        detections: detections,
        threat_detected: aiResult.threat_detected,
        confidence: aiResult.confidence,
        severity: aiResult.severity,
        event: aiResult.event,
        snapshot: snapshot,
        alert: alert,
        image_size: aiResult.image_size
      }
    });
  } catch (error) {
    console.error('AI analysis error:', error);

    if (error.isAIServiceError) {
      return res.status(error.statusCode || 503).json({
        success: false,
        message: 'AI service unavailable or failed to process image',
        error: error.message
      });
    }

    res.status(500).json({
      success: false,
      message: 'Failed to analyze image',
      error: error.message
    });
  }
};

/**
 * Process image through AI service and create alert if needed
 */
export const processImage = async (req, res) => {
  try {
    const { cameraId } = req.params;

    // Validate camera exists
    const camera = await Camera.findById(cameraId);
    if (!camera) {
      return res.status(404).json({
        success: false,
        message: 'Camera not found'
      });
    }

    // Check if file was uploaded
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'No image file provided'
      });
    }

    // Read image buffer
    const imageBuffer = await fs.readFile(req.file.path);

    // Call AI service for detection
    const aiResult = await aiServiceClient.detectImage(imageBuffer, {
      camera_id: cameraId
    });

    // Get settings for threshold comparison
    const settings = await Settings.getSettings();

    // Determine if we should create an alert based on business rules
    const shouldAlert = await shouldCreateAlert(aiResult, settings);

    let alert = null;
    let snapshot = null;

    if (shouldAlert) {
      // Save snapshot first
      snapshot = await Snapshot.create({
        camera: cameraId,
        imageUrl: `/uploads/snapshots/${req.file.filename}`,
        thumbnailUrl: `/uploads/snapshots/${req.file.filename}`, // TODO: Generate thumbnail
        filename: req.file.filename,
        fileSize: req.file.size,
        mimeType: req.file.mimetype,
        capturedAt: new Date(),
        metadata: {
          width: aiResult.image_size.width,
          height: aiResult.image_size.height,
          aiProcessed: true,
          aiConfidence: aiResult.confidence * 100
        }
      });

      // Create alert
      alert = await Alert.create({
        camera: cameraId,
        snapshot: snapshot._id,
        type: mapEventToType(aiResult.event),
        severity: aiResult.severity,
        status: 'open',
        description: generateAlertDescription(aiResult),
        detectedAt: new Date(),
        metadata: {
          confidence: aiResult.confidence * 100,
          boundingBox: aiResult.bounding_boxes.length > 0
            ? {
                x: aiResult.bounding_boxes[0].x_min,
                y: aiResult.bounding_boxes[0].y_min,
                width: aiResult.bounding_boxes[0].width,
                height: aiResult.bounding_boxes[0].height
              }
            : null
        }
      });

      // Populate references for response
      await alert.populate('camera', 'name location');
      await alert.populate('snapshot', 'imageUrl thumbnailUrl');
    } else {
      // No alert created, but save snapshot for reference
      snapshot = await Snapshot.create({
        camera: cameraId,
        imageUrl: `/uploads/snapshots/${req.file.filename}`,
        thumbnailUrl: `/uploads/snapshots/${req.file.filename}`,
        filename: req.file.filename,
        fileSize: req.file.size,
        mimeType: req.file.mimetype,
        capturedAt: new Date(),
        metadata: {
          width: aiResult.image_size.width,
          height: aiResult.image_size.height,
          aiProcessed: true,
          aiConfidence: aiResult.confidence * 100
        }
      });
    }

    res.json({
      success: true,
      data: {
        detection: aiResult,
        alert: alert,
        snapshot: snapshot,
        alert_created: shouldAlert
      }
    });
  } catch (error) {
    console.error('AI processing error:', error);

    // Check if it's an AI service error
    if (error.isAIServiceError) {
      return res.status(error.statusCode || 503).json({
        success: false,
        message: 'AI service unavailable or failed to process image',
        error: error.message
      });
    }

    res.status(500).json({
      success: false,
      message: 'Failed to process image',
      error: error.message
    });
  }
};

/**
 * Start stream monitoring for a camera
 */
export const startCameraStream = async (req, res) => {
  try {
    const { cameraId } = req.params;
    const { duration, frame_skip } = req.body;

    // Validate camera
    const camera = await Camera.findById(cameraId);
    if (!camera) {
      return res.status(404).json({
        success: false,
        message: 'Camera not found'
      });
    }

    // Check if AI is enabled for this camera
    if (!camera.aiEnabled) {
      return res.status(400).json({
        success: false,
        message: 'AI detection is not enabled for this camera'
      });
    }

    // Check if stream URL is configured
    if (!camera.streamUrl) {
      return res.status(400).json({
        success: false,
        message: 'No stream URL configured for this camera'
      });
    }

    // Prepare webhook callback URL for AI service to send detections
    const callbackUrl = `${process.env.BACKEND_URL || 'http://localhost:5000'}/api/v1/ai/webhook/detection`;

    // Start stream processing
    const result = await aiServiceClient.startStream(
      camera.streamUrl,
      cameraId,
      {
        duration: duration || 300,
        frame_skip: frame_skip || 5,
        callback_url: callbackUrl
      }
    );

    res.json({
      success: true,
      message: 'Stream monitoring started',
      data: result
    });
  } catch (error) {
    console.error('Stream start error:', error);

    if (error.isAIServiceError) {
      return res.status(error.statusCode || 503).json({
        success: false,
        message: 'Failed to start stream monitoring',
        error: error.message
      });
    }

    res.status(500).json({
      success: false,
      message: 'Failed to start stream monitoring',
      error: error.message
    });
  }
};

/**
 * Webhook endpoint for AI service to send detections
 * This is called by the AI service when it detects threats in a stream
 */
export const receiveDetectionWebhook = async (req, res) => {
  try {
    const detection = req.body;

    console.log('Received detection webhook:', detection);

    // Get settings for threshold comparison
    const settings = await Settings.getSettings();

    // Check if alert should be created based on business rules
    if (await shouldCreateAlert(detection, settings)) {
      // Create alert without snapshot (stream frame not saved)
      const alert = await Alert.create({
        camera: detection.camera_id,
        type: mapEventToType(detection.event),
        severity: detection.severity,
        status: 'open',
        description: `Stream detection: ${generateAlertDescription(detection)}`,
        detectedAt: new Date(detection.timestamp || Date.now()),
        metadata: {
          confidence: detection.confidence * 100,
          boundingBox: detection.bounding_boxes.length > 0
            ? {
                x: detection.bounding_boxes[0].x_min,
                y: detection.bounding_boxes[0].y_min,
                width: detection.bounding_boxes[0].width,
                height: detection.bounding_boxes[0].height
              }
            : null
        }
      });

      console.log(`Alert created from stream detection: ${alert._id}`);

      // TODO: Send notification (email, push, SMS based on settings)
      // await notificationService.sendAlert(alert);
    }

    // Always return success to AI service (don't fail webhook)
    res.json({
      success: true,
      message: 'Detection received'
    });
  } catch (error) {
    console.error('Webhook error:', error);

    // Don't fail webhook - AI service shouldn't retry on our errors
    res.status(200).json({
      success: false,
      error: error.message
    });
  }
};

/**
 * Get AI service status
 */
export const getAIStatus = async (req, res) => {
  try {
    const status = await aiServiceClient.getStatus();

    res.json({
      success: true,
      data: status
    });
  } catch (error) {
    console.error('AI status error:', error);

    res.status(503).json({
      success: false,
      message: 'AI service unavailable',
      error: error.message
    });
  }
};

/**
 * Get stream processing status
 */
export const getStreamStatus = async (req, res) => {
  try {
    const { taskId } = req.params;

    const status = await aiServiceClient.getStreamStatus(taskId);

    res.json({
      success: true,
      data: status
    });
  } catch (error) {
    console.error('Stream status error:', error);

    if (error.statusCode === 404) {
      return res.status(404).json({
        success: false,
        message: 'Stream task not found'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Failed to get stream status',
      error: error.message
    });
  }
};

/**
 * Stop stream processing
 */
export const stopCameraStream = async (req, res) => {
  try {
    const { taskId } = req.params;

    const result = await aiServiceClient.stopStream(taskId);

    res.json({
      success: true,
      message: 'Stream stopped',
      data: result
    });
  } catch (error) {
    console.error('Stream stop error:', error);

    if (error.statusCode === 404) {
      return res.status(404).json({
        success: false,
        message: 'Stream task not found'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Failed to stop stream',
      error: error.message
    });
  }
};

// ========== Helper Functions ==========

/**
 * Determine if an alert should be created based on detection and settings
 * @param {Object} detection - Detection result from AI service
 * @param {Object} settings - System settings with alert thresholds
 * @returns {Promise<boolean>} Whether to create alert
 */
async function shouldCreateAlert(detection, settings) {
  // No threat detected
  if (!detection.threat_detected) {
    return false;
  }

  const confidence = detection.confidence * 100;
  const event = detection.event.replace('_detected', '');

  // Map AI events to alert types
  const eventTypeMap = {
    'theft': 'theft',
    'product_picked': 'suspicious',
    'customer_bagpack': 'suspicious',
    'shopping_cart': 'suspicious',
    'normal': 'other',
    'product': 'other'
  };

  const alertType = eventTypeMap[event] || 'other';

  // Check against settings thresholds
  if (alertType === 'theft' && settings.alertThresholds.theft.enabled) {
    return confidence >= settings.alertThresholds.theft.confidence;
  }

  if (alertType === 'suspicious' && settings.alertThresholds.suspicious.enabled) {
    return confidence >= settings.alertThresholds.suspicious.confidence;
  }

  // Default: don't create alert for other types
  return false;
}

/**
 * Map AI event name to Alert type enum
 * @param {string} event - Event from AI service (e.g., "theft_detected")
 * @returns {string} Alert type
 */
function mapEventToType(event) {
  const eventMap = {
    'theft_detected': 'theft',
    'product_picked_detected': 'suspicious',
    'customer_bagpack_detected': 'suspicious',
    'shopping_cart_detected': 'suspicious',
    'no_threat': 'other',
    'normal_detected': 'other',
    'product_detected': 'other'
  };

  return eventMap[event] || 'other';
}

/**
 * Generate human-readable alert description
 * @param {Object} detection - Detection result
 * @returns {string} Description
 */
function generateAlertDescription(detection) {
  const numDetections = detection.num_detections;
  const confidence = (detection.confidence * 100).toFixed(1);
  const event = detection.event.replace('_detected', '').replace(/_/g, ' ');

  if (numDetections === 0) {
    return `No threats detected`;
  }

  return `Detected ${event} with ${confidence}% confidence (${numDetections} object${numDetections > 1 ? 's' : ''} detected)`;
}
