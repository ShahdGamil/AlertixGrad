import express from 'express';
import {
  getAllUsers,
  getUserById,
  createUser,
  updateUser,
  deleteUser
} from '../controllers/user.controller.js';
import { authenticate, authorize } from '../middleware/auth.middleware.js';
import { auditLog } from '../middleware/audit.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// Admin only routes
router.get('/', authorize('admin'), getAllUsers);
router.post('/', authorize('admin'), auditLog('user_create', 'User'), createUser);
router.get('/:id', authorize('admin'), getUserById);
router.put('/:id', authorize('admin'), auditLog('user_update', 'User'), updateUser);
router.delete('/:id', authorize('admin'), auditLog('user_delete', 'User'), deleteUser);

export default router;





