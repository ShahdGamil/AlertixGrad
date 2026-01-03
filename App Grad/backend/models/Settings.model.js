import mongoose from 'mongoose';

const settingsSchema = new mongoose.Schema({
  alertThresholds: {
    theft: {
      confidence: {
        type: Number,
        default: 75,
        min: 0,
        max: 100
      },
      enabled: {
        type: Boolean,
        default: true
      }
    },
    suspicious: {
      confidence: {
        type: Number,
        default: 60,
        min: 0,
        max: 100
      },
      enabled: {
        type: Boolean,
        default: true
      }
    },
    motion: {
      sensitivity: {
        type: Number,
        default: 50,
        min: 0,
        max: 100
      },
      enabled: {
        type: Boolean,
        default: true
      }
    }
  },
  notificationPreferences: {
    email: {
      enabled: {
        type: Boolean,
        default: true
      },
      criticalOnly: {
        type: Boolean,
        default: false
      }
    },
    push: {
      enabled: {
        type: Boolean,
        default: true
      },
      criticalOnly: {
        type: Boolean,
        default: false
      }
    },
    sms: {
      enabled: {
        type: Boolean,
        default: false
      },
      criticalOnly: {
        type: Boolean,
        default: true
      }
    }
  },
  systemSettings: {
    snapshotRetentionDays: {
      type: Number,
      default: 30
    },
    alertRetentionDays: {
      type: Number,
      default: 90
    },
    autoAcknowledgeAfter: {
      type: Number,
      default: 0 // 0 means disabled, value in hours
    }
  },
  updatedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Ensure only one settings document exists
settingsSchema.statics.getSettings = async function() {
  let settings = await this.findOne();
  if (!settings) {
    settings = await this.create({});
  }
  return settings;
};

export default mongoose.model('Settings', settingsSchema);





