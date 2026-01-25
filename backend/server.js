import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

// Import routes
import authRoutes from './routes/auth.routes.js';
import userRoutes from './routes/user.routes.js';
import cameraRoutes from './routes/camera.routes.js';
import alertRoutes from './routes/alert.routes.js';
import snapshotRoutes from './routes/snapshot.routes.js';
import reportRoutes from './routes/report.routes.js';
import settingsRoutes from './routes/settings.routes.js';
import billingRoutes from './routes/billing.routes.js';
import notificationRoutes from './routes/notification.routes.js';
import aiRoutes from './routes/ai.routes.js';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// Middleware
app.use(cors({
  origin: function (origin, callback) {
    // Allow requests with no origin (like mobile apps or curl requests)
    if (!origin) return callback(null, true);
    
    const allowedOrigins = [
      process.env.CORS_ORIGIN || 'http://localhost:3000',
      'http://localhost:19006', // Expo Web default
      'http://localhost:8082',  // Expo alternative port
      /^http:\/\/localhost:\d+$/, // Any localhost port
      /^http:\/\/192\.168\.\d+\.\d+:\d+$/ // Local network IPs
    ];
    
    if (allowedOrigins.some(allowed => {
      if (allowed instanceof RegExp) {
        return allowed.test(origin);
      }
      return allowed === origin;
    })) {
      callback(null, true);
    } else {
      callback(null, true); // Allow all for development
    }
  },
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve uploaded files
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'InstaGuard AI Backend is running' });
});

// API Routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/users', userRoutes);
app.use('/api/v1/cameras', cameraRoutes);
app.use('/api/v1/alerts', alertRoutes);
app.use('/api/v1/snapshots', snapshotRoutes);
app.use('/api/v1/reports', reportRoutes);
app.use('/api/v1/settings', settingsRoutes);
app.use('/api/v1/billing', billingRoutes);
app.use('/api/v1/notifications', notificationRoutes);
app.use('/api/v1/ai', aiRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    success: false,
    message: err.message || 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route not found'
  });
});

// Connect to MongoDB
const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/instaguard-ai');
    console.log('MongoDB connected successfully');
  } catch (error) {
    console.error('MongoDB connection error:', error);
    process.exit(1);
  }
};

// Ensure upload directories exist
const ensureUploadDirectories = () => {
  const uploadDirs = [
    path.join(__dirname, 'uploads'),
    path.join(__dirname, 'uploads', 'snapshots')
  ];

  uploadDirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`Created directory: ${dir}`);
    }
  });
};

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, async () => {
  await connectDB();
  ensureUploadDirectories();
  console.log(`Server running on port ${PORT}`);
  console.log(`AI Service URL: ${process.env.AI_SERVICE_URL || 'http://localhost:5001'}`);
});

export default app;

