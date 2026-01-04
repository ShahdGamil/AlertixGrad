import express from 'express';
import {
  getNotifications,
  markAsRead,
  getUnreadCount
} from '../controllers/notification.controller.js';
import { authenticate } from '../middleware/auth.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

router.get('/', getNotifications);
router.get('/unread-count', getUnreadCount);
router.post('/:id/read', markAsRead);

export default router;





