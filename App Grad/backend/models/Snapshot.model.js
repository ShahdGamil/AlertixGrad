import mongoose from 'mongoose';

const snapshotSchema = new mongoose.Schema({
  camera: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Camera',
    required: [true, 'Camera is required']
  },
  alert: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Alert'
  },
  imageUrl: {
    type: String,
    required: [true, 'Image URL is required']
  },
  thumbnailUrl: {
    type: String
  },
  filename: {
    type: String,
    required: true
  },
  fileSize: {
    type: Number
  },
  mimeType: {
    type: String,
    default: 'image/jpeg'
  },
  capturedAt: {
    type: Date,
    default: Date.now
  },
  tags: [{
    type: String
  }],
  metadata: {
    width: Number,
    height: Number,
    aiProcessed: {
      type: Boolean,
      default: false
    },
    aiConfidence: Number
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Index for efficient queries
snapshotSchema.index({ camera: 1, capturedAt: -1 });
snapshotSchema.index({ alert: 1 });

export default mongoose.model('Snapshot', snapshotSchema);





