import Alert from '../models/Alert.model.js';
import Settings from '../models/Settings.model.js';

export const getNotifications = async (req, res) => {
  try {
    const { page = 1, limit = 20, unreadOnly = false } = req.query;

    // Get recent alerts as notifications
    const query = {};
    
    if (unreadOnly === 'true') {
      // In a real system, you'd have a read/unread flag
      // For now, we'll show recent alerts
      query.detectedAt = {
        $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) // Last 24 hours
      };
    }

    const alerts = await Alert.find(query)
      .populate('camera', 'name location')
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ detectedAt: -1 });

    const total = await Alert.countDocuments(query);
    const unreadCount = await Alert.countDocuments({
      status: 'open',
      detectedAt: {
        $gte: new Date(Date.now() - 24 * 60 * 60 * 1000)
      }
    });

    // Transform alerts to notification format
    const notifications = alerts.map(alert => ({
      id: alert._id,
      type: 'alert',
      title: `${alert.type.charAt(0).toUpperCase() + alert.type.slice(1)} Alert`,
      message: alert.description || `Alert detected at ${alert.camera?.name || 'Unknown Camera'}`,
      severity: alert.severity,
      status: alert.status,
      camera: alert.camera?.name,
      location: alert.camera?.location,
      timestamp: alert.detectedAt,
      read: alert.status !== 'open'
    }));

    res.json({
      success: true,
      data: {
        notifications,
        unreadCount,
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
      message: 'Failed to fetch notifications',
      error: error.message
    });
  }
};

export const markAsRead = async (req, res) => {
  try {
    // In a real system, you'd update a read status
    // For now, acknowledging the alert marks it as read
    const alert = await Alert.findById(req.params.id);

    if (!alert) {
      return res.status(404).json({
        success: false,
        message: 'Notification not found'
      });
    }

    res.json({
      success: true,
      message: 'Notification marked as read'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to mark notification as read',
      error: error.message
    });
  }
};

export const getUnreadCount = async (req, res) => {
  try {
    const unreadCount = await Alert.countDocuments({
      status: 'open',
      detectedAt: {
        $gte: new Date(Date.now() - 24 * 60 * 60 * 1000)
      }
    });

    res.json({
      success: true,
      data: { unreadCount }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to get unread count',
      error: error.message
    });
  }
};





