import express from 'express';
import {
  getSettings,
  updateSettings
} from '../controllers/settings.controller.js';
import { authenticate, authorize } from '../middleware/auth.middleware.js';
import { auditLog } from '../middleware/audit.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// All authenticated users can view settings
router.get('/', getSettings);

// Admin only can update settings
router.put('/', authorize('admin'), auditLog('settings_update', 'Settings'), updateSettings);

export default router;





