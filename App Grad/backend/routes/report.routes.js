import express from 'express';
import {
  getAllReports,
  getReportById,
  generateReport,
  downloadReport
} from '../controllers/report.controller.js';
import { authenticate, authorize } from '../middleware/auth.middleware.js';
import { auditLog } from '../middleware/audit.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// Admin and Operator can generate and view reports
router.get('/', authorize('admin', 'operator', 'viewer'), getAllReports);
router.get('/:id', authorize('admin', 'operator', 'viewer'), getReportById);
router.post('/', authorize('admin', 'operator'), auditLog('report_generate', 'Report'), generateReport);
router.get('/:id/download', authorize('admin', 'operator', 'viewer'), downloadReport);

export default router;





