import Snapshot from '../models/Snapshot.model.js';
import Alert from '../models/Alert.model.js';
import path from 'path';
import fs from 'fs/promises';

export const getAllSnapshots = async (req, res) => {
  try {
    const { 
      page = 1, 
      limit = 20, 
      camera, 
      alert,
      startDate,
      endDate,
      tags
    } = req.query;
    
    const query = {};

    if (camera) query.camera = camera;
    if (alert) query.alert = alert;
    
    if (startDate || endDate) {
      query.capturedAt = {};
      if (startDate) query.capturedAt.$gte = new Date(startDate);
      if (endDate) query.capturedAt.$lte = new Date(endDate);
    }
    
    if (tags) {
      query.tags = { $in: Array.isArray(tags) ? tags : [tags] };
    }

    const snapshots = await Snapshot.find(query)
      .populate('camera', 'name location')
      .populate('alert', 'type severity status')
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ capturedAt: -1 });

    const total = await Snapshot.countDocuments(query);

    res.json({
      success: true,
      data: {
        snapshots,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch snapshots',
      error: error.message
    });
  }
};

export const getSnapshotById = async (req, res) => {
  try {
    const snapshot = await Snapshot.findById(req.params.id)
      .populate('camera', 'name location')
      .populate('alert', 'type severity status description');

    if (!snapshot) {
      return res.status(404).json({
        success: false,
        message: 'Snapshot not found'
      });
    }

    res.json({
      success: true,
      data: { snapshot }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch snapshot',
      error: error.message
    });
  }
};

export const createSnapshot = async (req, res) => {
  try {
    const snapshot = await Snapshot.create(req.body);

    await snapshot.populate('camera', 'name location');
    await snapshot.populate('alert', 'type severity');

    res.status(201).json({
      success: true,
      message: 'Snapshot created successfully',
      data: { snapshot }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to create snapshot',
      error: error.message
    });
  }
};

export const deleteSnapshot = async (req, res) => {
  try {
    const snapshot = await Snapshot.findById(req.params.id);

    if (!snapshot) {
      return res.status(404).json({
        success: false,
        message: 'Snapshot not found'
      });
    }

    // Delete file if exists
    if (snapshot.imageUrl) {
      try {
        const filePath = path.join(process.cwd(), snapshot.imageUrl);
        await fs.unlink(filePath);
      } catch (error) {
        console.error('Error deleting file:', error);
      }
    }

    await Snapshot.findByIdAndDelete(req.params.id);

    res.json({
      success: true,
      message: 'Snapshot deleted successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to delete snapshot',
      error: error.message
    });
  }
};

export const downloadSnapshot = async (req, res) => {
  try {
    const snapshot = await Snapshot.findById(req.params.id);

    if (!snapshot) {
      return res.status(404).json({
        success: false,
        message: 'Snapshot not found'
      });
    }

    const filePath = path.join(process.cwd(), snapshot.imageUrl);
    
    try {
      await fs.access(filePath);
      res.download(filePath, snapshot.filename || 'snapshot.jpg');
    } catch (error) {
      res.status(404).json({
        success: false,
        message: 'File not found'
      });
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to download snapshot',
      error: error.message
    });
  }
};





