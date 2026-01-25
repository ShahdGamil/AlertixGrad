import Alert from '../models/Alert.model.js';
import Snapshot from '../models/Snapshot.model.js';

export const getAllAlerts = async (req, res) => {
  try {
    const { 
      page = 1, 
      limit = 20, 
      status, 
      severity, 
      type, 
      camera,
      startDate,
      endDate
    } = req.query;
    
    const query = {};

    if (status) query.status = status;
    if (severity) query.severity = severity;
    if (type) query.type = type;
    if (camera) query.camera = camera;
    
    if (startDate || endDate) {
      query.detectedAt = {};
      if (startDate) query.detectedAt.$gte = new Date(startDate);
      if (endDate) query.detectedAt.$lte = new Date(endDate);
    }

    const alerts = await Alert.find(query)
      .populate('camera', 'name location status')
      .populate('snapshot', 'imageUrl thumbnailUrl')
      .populate('acknowledgedBy', 'name email')
      .populate('closedBy', 'name email')
      .populate('notes.user', 'name email')
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ detectedAt: -1 });

    const total = await Alert.countDocuments(query);
    const openCount = await Alert.countDocuments({ status: 'open' });
    const acknowledgedCount = await Alert.countDocuments({ status: 'acknowledged' });
    const closedCount = await Alert.countDocuments({ status: 'closed' });

    res.json({
      success: true,
      data: {
        alerts,
        stats: {
          total,
          open: openCount,
          acknowledged: acknowledgedCount,
          closed: closedCount
        },
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
      message: 'Failed to fetch alerts',
      error: error.message
    });
  }
};

export const getAlertById = async (req, res) => {
  try {
    const alert = await Alert.findById(req.params.id)
      .populate('camera', 'name location status streamUrl')
      .populate('snapshot', 'imageUrl thumbnailUrl filename')
      .populate('acknowledgedBy', 'name email')
      .populate('closedBy', 'name email')
      .populate('notes.user', 'name email');

    if (!alert) {
      return res.status(404).json({
        success: false,
        message: 'Alert not found'
      });
    }

    res.json({
      success: true,
      data: { alert }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch alert',
      error: error.message
    });
  }
};

export const createAlert = async (req, res) => {
  try {
    const alert = await Alert.create(req.body);

    await alert.populate('camera', 'name location');
    await alert.populate('snapshot', 'imageUrl thumbnailUrl');

    res.status(201).json({
      success: true,
      message: 'Alert created successfully',
      data: { alert }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to create alert',
      error: error.message
    });
  }
};

export const acknowledgeAlert = async (req, res) => {
  try {
    const alert = await Alert.findById(req.params.id);

    if (!alert) {
      return res.status(404).json({
        success: false,
        message: 'Alert not found'
      });
    }

    if (alert.status === 'closed') {
      return res.status(400).json({
        success: false,
        message: 'Cannot acknowledge a closed alert'
      });
    }

    alert.status = 'acknowledged';
    alert.acknowledgedBy = req.user._id;
    alert.acknowledgedAt = new Date();
    await alert.save();

    await alert.populate('acknowledgedBy', 'name email');

    res.json({
      success: true,
      message: 'Alert acknowledged successfully',
      data: { alert }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to acknowledge alert',
      error: error.message
    });
  }
};

export const closeAlert = async (req, res) => {
  try {
    const alert = await Alert.findById(req.params.id);

    if (!alert) {
      return res.status(404).json({
        success: false,
        message: 'Alert not found'
      });
    }

    alert.status = 'closed';
    alert.closedBy = req.user._id;
    alert.closedAt = new Date();
    await alert.save();

    await alert.populate('closedBy', 'name email');

    res.json({
      success: true,
      message: 'Alert closed successfully',
      data: { alert }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to close alert',
      error: error.message
    });
  }
};

export const addNoteToAlert = async (req, res) => {
  try {
    const { note } = req.body;

    if (!note || !note.trim()) {
      return res.status(400).json({
        success: false,
        message: 'Note is required'
      });
    }

    const alert = await Alert.findById(req.params.id);

    if (!alert) {
      return res.status(404).json({
        success: false,
        message: 'Alert not found'
      });
    }

    alert.notes.push({
      user: req.user._id,
      note: note.trim()
    });

    await alert.save();
    await alert.populate('notes.user', 'name email');

    res.json({
      success: true,
      message: 'Note added successfully',
      data: { alert }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to add note',
      error: error.message
    });
  }
};

export const deleteAlert = async (req, res) => {
  try {
    const alert = await Alert.findById(req.params.id);

    if (!alert) {
      return res.status(404).json({
        success: false,
        message: 'Alert not found'
      });
    }

    await Alert.findByIdAndDelete(req.params.id);

    res.json({
      success: true,
      message: 'Alert deleted successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to delete alert',
      error: error.message
    });
  }
};





