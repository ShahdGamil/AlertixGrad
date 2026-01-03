import mongoose from 'mongoose';

const reportSchema = new mongoose.Schema({
  title: {
    type: String,
    required: [true, 'Report title is required'],
    trim: true
  },
  type: {
    type: String,
    enum: ['alerts', 'cameras', 'snapshots', 'custom'],
    required: true
  },
  generatedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  dateRange: {
    start: {
      type: Date,
      required: true
    },
    end: {
      type: Date,
      required: true
    }
  },
  filters: {
    cameras: [{
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Camera'
    }],
    alertTypes: [String],
    severities: [String],
    statuses: [String]
  },
  format: {
    type: String,
    enum: ['pdf', 'csv'],
    default: 'pdf'
  },
  fileUrl: {
    type: String
  },
  fileSize: {
    type: Number
  },
  status: {
    type: String,
    enum: ['pending', 'generating', 'completed', 'failed'],
    default: 'pending'
  },
  metadata: {
    totalRecords: Number,
    generatedAt: Date
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

export default mongoose.model('Report', reportSchema);





