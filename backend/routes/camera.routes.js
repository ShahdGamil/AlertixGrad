import express from 'express';
import {
  getAllCameras,
  getCameraById,
  createCamera,
  updateCamera,
  deleteCamera,
  updateCameraStatus
} from '../controllers/camera.controller.js';
import { authenticate, authorize } from '../middleware/auth.middleware.js';
import { auditLog } from '../middleware/audit.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// All authenticated users can view cameras
router.get('/', getAllCameras);
router.get('/:id', getCameraById);

// Admin and Operator can create/update cameras
router.post('/', authorize('admin', 'operator'), auditLog('camera_create', 'Camera'), createCamera);
router.put('/:id', authorize('admin', 'operator'), auditLog('camera_update', 'Camera'), updateCamera);
router.patch('/:id/status', authorize('admin', 'operator'), updateCameraStatus);

// Admin only routes
router.delete('/:id', authorize('admin'), auditLog('camera_delete', 'Camera'), deleteCamera);

export default router;





