import mongoose from 'mongoose';

const alertSchema = new mongoose.Schema({
  camera: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Camera',
    required: [true, 'Camera is required']
  },
  snapshot: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Snapshot'
  },
  type: {
    type: String,
    enum: ['theft', 'suspicious', 'motion', 'other'],
    default: 'suspicious'
  },
  severity: {
    type: String,
    enum: ['low', 'medium', 'high', 'critical'],
    default: 'medium'
  },
  status: {
    type: String,
    enum: ['open', 'acknowledged', 'closed'],
    default: 'open'
  },
  description: {
    type: String,
    trim: true
  },
  detectedAt: {
    type: Date,
    default: Date.now
  },
  acknowledgedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  acknowledgedAt: {
    type: Date
  },
  closedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  closedAt: {
    type: Date
  },
  notes: [{
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    note: {
      type: String,
      required: true
    },
    createdAt: {
      type: Date,
      default: Date.now
    }
  }],
  metadata: {
    confidence: {
      type: Number,
      min: 0,
      max: 100
    },
    boundingBox: {
      x: Number,
      y: Number,
      width: Number,
      height: Number
    }
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Index for efficient queries
alertSchema.index({ camera: 1, status: 1, detectedAt: -1 });
alertSchema.index({ status: 1, detectedAt: -1 });

export default mongoose.model('Alert', alertSchema);





