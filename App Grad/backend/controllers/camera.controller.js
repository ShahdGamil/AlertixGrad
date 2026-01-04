import Camera from '../models/Camera.model.js';

export const getAllCameras = async (req, res) => {
  try {
    const { page = 1, limit = 20, status, search } = req.query;
    const query = {};

    if (status) query.status = status;
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { location: { $regex: search, $options: 'i' } }
      ];
    }

    const cameras = await Camera.find(query)
      .populate('createdBy', 'name email')
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ createdAt: -1 });

    const total = await Camera.countDocuments(query);
    const onlineCount = await Camera.countDocuments({ status: 'online', isActive: true });

    res.json({
      success: true,
      data: {
        cameras,
        stats: {
          total,
          online: onlineCount,
          offline: total - onlineCount
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
      message: 'Failed to fetch cameras',
      error: error.message
    });
  }
};

export const getCameraById = async (req, res) => {
  try {
    const camera = await Camera.findById(req.params.id)
      .populate('createdBy', 'name email');

    if (!camera) {
      return res.status(404).json({
        success: false,
        message: 'Camera not found'
      });
    }

    res.json({
      success: true,
      data: { camera }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch camera',
      error: error.message
    });
  }
};

export const createCamera = async (req, res) => {
  try {
    const camera = await Camera.create({
      ...req.body,
      createdBy: req.user._id
    });

    await camera.populate('createdBy', 'name email');

    res.status(201).json({
      success: true,
      message: 'Camera created successfully',
      data: { camera }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to create camera',
      error: error.message
    });
  }
};

export const updateCamera = async (req, res) => {
  try {
    const camera = await Camera.findById(req.params.id);

    if (!camera) {
      return res.status(404).json({
        success: false,
        message: 'Camera not found'
      });
    }

    // Operators can only update limited fields
    if (req.user.role === 'operator') {
      const allowedFields = ['name', 'location', 'status'];
      const updates = {};
      allowedFields.forEach(field => {
        if (req.body[field] !== undefined) {
          updates[field] = req.body[field];
        }
      });
      Object.assign(camera, updates);
    } else {
      // Admin can update all fields
      Object.assign(camera, req.body);
    }

    await camera.save();
    await camera.populate('createdBy', 'name email');

    res.json({
      success: true,
      message: 'Camera updated successfully',
      data: { camera }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to update camera',
      error: error.message
    });
  }
};

export const deleteCamera = async (req, res) => {
  try {
    const camera = await Camera.findById(req.params.id);

    if (!camera) {
      return res.status(404).json({
        success: false,
        message: 'Camera not found'
      });
    }

    await Camera.findByIdAndDelete(req.params.id);

    res.json({
      success: true,
      message: 'Camera deleted successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to delete camera',
      error: error.message
    });
  }
};

export const updateCameraStatus = async (req, res) => {
  try {
    const { status } = req.body;
    const camera = await Camera.findById(req.params.id);

    if (!camera) {
      return res.status(404).json({
        success: false,
        message: 'Camera not found'
      });
    }

    camera.status = status;
    camera.lastSeen = new Date();
    await camera.save();

    res.json({
      success: true,
      message: 'Camera status updated successfully',
      data: { camera }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to update camera status',
      error: error.message
    });
  }
};





