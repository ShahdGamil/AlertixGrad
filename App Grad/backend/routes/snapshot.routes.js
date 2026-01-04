import express from 'express';
import {
  getAllSnapshots,
  getSnapshotById,
  createSnapshot,
  deleteSnapshot,
  downloadSnapshot
} from '../controllers/snapshot.controller.js';
import { authenticate, authorize } from '../middleware/auth.middleware.js';
import { auditLog } from '../middleware/audit.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// All authenticated users can view snapshots
router.get('/', getAllSnapshots);
router.get('/:id', getSnapshotById);
router.get('/:id/download', downloadSnapshot);

// Admin only routes
router.post('/', authorize('admin'), createSnapshot);
router.delete('/:id', authorize('admin'), auditLog('snapshot_delete', 'Snapshot'), deleteSnapshot);

export default router;





