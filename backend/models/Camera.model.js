import mongoose from 'mongoose';

const cameraSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Camera name is required'],
    trim: true
  },
  location: {
    type: String,
    required: [true, 'Location is required'],
    trim: true
  },
  ipAddress: {
    type: String,
    required: [true, 'IP address is required'],
    match: [/^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/, 'Please provide a valid IP address']
  },
  port: {
    type: Number,
    default: 8080
  },
  streamUrl: {
    type: String,
    required: [true, 'Stream URL is required']
  },
  status: {
    type: String,
    enum: ['online', 'offline', 'maintenance'],
    default: 'offline'
  },
  isActive: {
    type: Boolean,
    default: true
  },
  aiEnabled: {
    type: Boolean,
    default: true
  },
  lastSeen: {
    type: Date,
    default: Date.now
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
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

export default mongoose.model('Camera', cameraSchema);





