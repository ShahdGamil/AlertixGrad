import mongoose from 'mongoose';
import dotenv from 'dotenv';
import User from '../models/User.model.js';
import Camera from '../models/Camera.model.js';
import Alert from '../models/Alert.model.js';
import Snapshot from '../models/Snapshot.model.js';
import Settings from '../models/Settings.model.js';

dotenv.config();

const seedData = async () => {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/instaguard-ai');
    console.log('Connected to MongoDB');

    // Clear existing data
    await User.deleteMany({});
    await Camera.deleteMany({});
    await Alert.deleteMany({});
    await Snapshot.deleteMany({});
    await Settings.deleteMany({});
    console.log('Cleared existing data');

    // Create users
    const admin = await User.create({
      name: 'Admin User',
      email: 'admin@instaguard.ai',
      password: 'admin123',
      role: 'admin',
      isActive: true
    });

    const operator = await User.create({
      name: 'Operator User',
      email: 'operator@instaguard.ai',
      password: 'operator123',
      role: 'operator',
      isActive: true
    });

    const viewer = await User.create({
      name: 'Viewer User',
      email: 'viewer@instaguard.ai',
      password: 'viewer123',
      role: 'viewer',
      isActive: true
    });

    console.log('Created users');

    // Create cameras
    const frontDoorCamera = await Camera.create({
      name: 'Front Door',
      location: 'Main Entrance',
      ipAddress: '192.168.1.100',
      port: 8080,
      streamUrl: 'rtsp://192.168.1.100:8080/stream',
      status: 'online',
      isActive: true,
      aiEnabled: true,
      createdBy: admin._id,
      lastSeen: new Date()
    });

    const aisle3Camera = await Camera.create({
      name: 'Aisle 3',
      location: 'Aisle 3 - Electronics Section',
      ipAddress: '192.168.1.101',
      port: 8080,
      streamUrl: 'rtsp://192.168.1.101:8080/stream',
      status: 'online',
      isActive: true,
      aiEnabled: true,
      createdBy: admin._id,
      lastSeen: new Date()
    });

    console.log('Created cameras');

    // Create snapshots
    const snapshots = [];
    for (let i = 0; i < 10; i++) {
      const snapshot = await Snapshot.create({
        camera: i % 2 === 0 ? frontDoorCamera._id : aisle3Camera._id,
        imageUrl: `/uploads/snapshots/snapshot-${i + 1}.jpg`,
        thumbnailUrl: `/uploads/snapshots/thumbnails/thumbnail-${i + 1}.jpg`,
        filename: `snapshot-${i + 1}.jpg`,
        fileSize: 1024 * 500 + Math.random() * 1024 * 500,
        mimeType: 'image/jpeg',
        capturedAt: new Date(Date.now() - i * 60 * 60 * 1000),
        tags: i % 3 === 0 ? ['theft', 'suspicious'] : ['motion'],
        metadata: {
          width: 1920,
          height: 1080,
          aiProcessed: true,
          aiConfidence: 75 + Math.random() * 20
        }
      });
      snapshots.push(snapshot);
    }

    console.log('Created snapshots');

    // Create alerts
    const alertTypes = ['theft', 'suspicious', 'motion'];
    const severities = ['low', 'medium', 'high', 'critical'];
    const statuses = ['open', 'acknowledged', 'closed'];

    const alerts = [];
    for (let i = 0; i < 15; i++) {
      const alertType = alertTypes[Math.floor(Math.random() * alertTypes.length)];
      const severity = severities[Math.floor(Math.random() * severities.length)];
      const status = statuses[Math.floor(Math.random() * statuses.length)];
      const camera = i % 2 === 0 ? frontDoorCamera._id : aisle3Camera._id;
      const snapshot = snapshots[i % snapshots.length];

      const alertData = {
        camera,
        snapshot: snapshot._id,
        type: alertType,
        severity,
        status,
        description: `${alertType.charAt(0).toUpperCase() + alertType.slice(1)} activity detected at ${i % 2 === 0 ? 'Front Door' : 'Aisle 3'}`,
        detectedAt: new Date(Date.now() - i * 2 * 60 * 60 * 1000),
        metadata: {
          confidence: 70 + Math.random() * 25,
          boundingBox: {
            x: Math.random() * 100,
            y: Math.random() * 100,
            width: 50 + Math.random() * 100,
            height: 50 + Math.random() * 100
          }
        }
      };

      if (status === 'acknowledged') {
        alertData.acknowledgedBy = operator._id;
        alertData.acknowledgedAt = new Date(Date.now() - i * 2 * 60 * 60 * 1000 + 30 * 60 * 1000);
      }

      if (status === 'closed') {
        alertData.acknowledgedBy = operator._id;
        alertData.acknowledgedAt = new Date(Date.now() - i * 2 * 60 * 60 * 1000 + 30 * 60 * 1000);
        alertData.closedBy = operator._id;
        alertData.closedAt = new Date(Date.now() - i * 2 * 60 * 60 * 1000 + 60 * 60 * 1000);
        alertData.notes = [{
          user: operator._id,
          note: 'Issue resolved. False alarm.',
          createdAt: new Date(Date.now() - i * 2 * 60 * 60 * 1000 + 60 * 60 * 1000)
        }];
      } else if (status === 'acknowledged') {
        alertData.notes = [{
          user: operator._id,
          note: 'Investigating the incident.',
          createdAt: new Date(Date.now() - i * 2 * 60 * 60 * 1000 + 30 * 60 * 1000)
        }];
      }

      const alert = await Alert.create(alertData);
      alerts.push(alert);
    }

    console.log('Created alerts');

    // Create default settings
    await Settings.create({
      alertThresholds: {
        theft: {
          confidence: 75,
          enabled: true
        },
        suspicious: {
          confidence: 60,
          enabled: true
        },
        motion: {
          sensitivity: 50,
          enabled: true
        }
      },
      notificationPreferences: {
        email: {
          enabled: true,
          criticalOnly: false
        },
        push: {
          enabled: true,
          criticalOnly: false
        },
        sms: {
          enabled: false,
          criticalOnly: true
        }
      },
      systemSettings: {
        snapshotRetentionDays: 30,
        alertRetentionDays: 90,
        autoAcknowledgeAfter: 0
      },
      updatedBy: admin._id
    });

    console.log('Created settings');

    console.log('\n✅ Seed data created successfully!');
    console.log('\nSample login credentials:');
    console.log('Admin: admin@instaguard.ai / admin123');
    console.log('Operator: operator@instaguard.ai / operator123');
    console.log('Viewer: viewer@instaguard.ai / viewer123');
    console.log('\nCameras created:');
    console.log('- Front Door (192.168.1.100)');
    console.log('- Aisle 3 (192.168.1.101)');
    console.log('\nAlerts created: 15');
    console.log('Snapshots created: 10');

    process.exit(0);
  } catch (error) {
    console.error('Error seeding data:', error);
    process.exit(1);
  }
};

seedData();





