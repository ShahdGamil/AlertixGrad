import express from 'express';
import {
  getBillingInfo,
  getInvoices
} from '../controllers/billing.controller.js';
import { authenticate, authorize } from '../middleware/auth.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authenticate);

// Admin only routes
router.get('/', authorize('admin'), getBillingInfo);
router.get('/invoices', authorize('admin'), getInvoices);

export default router;





