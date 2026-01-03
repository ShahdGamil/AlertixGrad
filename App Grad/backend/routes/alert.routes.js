import express from 'express';
import {
  getAllAlerts,
  getAlertById,
  createAlert,
  acknowledgeAlert,
  closeAlert,
  addNoteToAlert,
  deleteAlert
} from '../controllers/alert.controller.js';
import { authenticate, authorize } from '../middleware/auth.middleware.js';
import { auditLog } from '../middleware/audit.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// All authenticated users can view alerts
router.get('/', getAllAlerts);
router.get('/:id', getAlertById);

// Admin and Operator can acknowledge/close alerts and add notes
router.post('/:id/acknowledge', authorize('admin', 'operator'), auditLog('alert_acknowledge', 'Alert'), acknowledgeAlert);
router.post('/:id/close', authorize('admin', 'operator'), auditLog('alert_close', 'Alert'), closeAlert);
router.post('/:id/notes', authorize('admin', 'operator'), addNoteToAlert);

// Admin only routes
router.post('/', authorize('admin'), createAlert);
router.delete('/:id', authorize('admin'), auditLog('alert_delete', 'Alert'), deleteAlert);

export default router;





