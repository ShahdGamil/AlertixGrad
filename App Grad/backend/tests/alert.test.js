import request from 'supertest';
import app from '../server.js';
import User from '../models/User.model.js';
import Camera from '../models/Camera.model.js';
import Alert from '../models/Alert.model.js';
import mongoose from 'mongoose';
import { generateToken } from '../utils/generateToken.js';

describe('Alert Tests', () => {
  let adminToken;
  let operatorToken;
  let adminUser;
  let operatorUser;
  let camera;

  beforeAll(async () => {
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/instaguard-ai-test');
  });

  afterAll(async () => {
    await mongoose.connection.close();
  });

  beforeEach(async () => {
    // Clear data
    await User.deleteMany({});
    await Camera.deleteMany({});
    await Alert.deleteMany({});

    // Create test users
    adminUser = await User.create({
      name: 'Admin User',
      email: 'admin@test.com',
      password: 'password123',
      role: 'admin'
    });

    operatorUser = await User.create({
      name: 'Operator User',
      email: 'operator@test.com',
      password: 'password123',
      role: 'operator'
    });

    adminToken = generateToken(adminUser._id);
    operatorToken = generateToken(operatorUser._id);

    // Create test camera
    camera = await Camera.create({
      name: 'Test Camera',
      location: 'Test Location',
      ipAddress: '192.168.1.100',
      streamUrl: 'rtsp://test',
      createdBy: adminUser._id
    });
  });

  describe('GET /api/v1/alerts', () => {
    it('should get all alerts for authenticated user', async () => {
      await Alert.create({
        camera: camera._id,
        type: 'theft',
        severity: 'high',
        status: 'open'
      });

      const response = await request(app)
        .get('/api/v1/alerts')
        .set('Authorization', `Bearer ${adminToken}`);

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.alerts).toHaveLength(1);
    });

    it('should require authentication', async () => {
      const response = await request(app)
        .get('/api/v1/alerts');

      expect(response.status).toBe(401);
    });
  });

  describe('POST /api/v1/alerts/:id/acknowledge', () => {
    it('should acknowledge alert as operator', async () => {
      const alert = await Alert.create({
        camera: camera._id,
        type: 'theft',
        severity: 'high',
        status: 'open'
      });

      const response = await request(app)
        .post(`/api/v1/alerts/${alert._id}/acknowledge`)
        .set('Authorization', `Bearer ${operatorToken}`);

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      
      const updatedAlert = await Alert.findById(alert._id);
      expect(updatedAlert.status).toBe('acknowledged');
      expect(updatedAlert.acknowledgedBy.toString()).toBe(operatorUser._id.toString());
    });
  });
});





