import Settings from '../models/Settings.model.js';

export const getSettings = async (req, res) => {
  try {
    const settings = await Settings.getSettings();

    res.json({
      success: true,
      data: { settings }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch settings',
      error: error.message
    });
  }
};

export const updateSettings = async (req, res) => {
  try {
    const settings = await Settings.getSettings();

    const { alertThresholds, notificationPreferences, systemSettings } = req.body;

    if (alertThresholds) {
      if (alertThresholds.theft) {
        settings.alertThresholds.theft = {
          ...settings.alertThresholds.theft,
          ...alertThresholds.theft
        };
      }
      if (alertThresholds.suspicious) {
        settings.alertThresholds.suspicious = {
          ...settings.alertThresholds.suspicious,
          ...alertThresholds.suspicious
        };
      }
      if (alertThresholds.motion) {
        settings.alertThresholds.motion = {
          ...settings.alertThresholds.motion,
          ...alertThresholds.motion
        };
      }
    }

    if (notificationPreferences) {
      if (notificationPreferences.email) {
        settings.notificationPreferences.email = {
          ...settings.notificationPreferences.email,
          ...notificationPreferences.email
        };
      }
      if (notificationPreferences.push) {
        settings.notificationPreferences.push = {
          ...settings.notificationPreferences.push,
          ...notificationPreferences.push
        };
      }
      if (notificationPreferences.sms) {
        settings.notificationPreferences.sms = {
          ...settings.notificationPreferences.sms,
          ...notificationPreferences.sms
        };
      }
    }

    if (systemSettings) {
      settings.systemSettings = {
        ...settings.systemSettings,
        ...systemSettings
      };
    }

    settings.updatedBy = req.user._id;
    settings.updatedAt = new Date();
    await settings.save();

    res.json({
      success: true,
      message: 'Settings updated successfully',
      data: { settings }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to update settings',
      error: error.message
    });
  }
};





