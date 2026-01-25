import { Platform } from 'react-native';
import { savePushToken, getPushToken } from '../utils/secureStorage';

// Web-compatible: Only import Expo modules on native platforms
let Notifications = null;
let Device = null;
let Constants = null;

if (Platform.OS !== 'web') {
  try {
    Notifications = require('expo-notifications');
    Device = require('expo-device');
    Constants = require('expo-constants').default;
  } catch (e) {
    console.warn('Expo modules not available on web');
  }
}

/**
 * Push Notifications Service
 *
 * Handles registration and management of push notifications for the mobile app.
 *
 * Features:
 * - Register for push notifications
 * - Handle incoming notifications
 * - Send notification tokens to backend
 * - Configure notification behavior
 *
 * Platform support:
 * - iOS: Uses APNs (Apple Push Notification service)
 * - Android: Uses FCM (Firebase Cloud Messaging)
 * - Web: Limited support via service workers
 */

// Configure how notifications are presented when app is in foreground (only on native)
if (Notifications) {
  Notifications.setNotificationHandler({
    handleNotification: async () => ({
      shouldShowAlert: true,
      shouldPlaySound: true,
      shouldSetBadge: true,
    }),
  });
}

/**
 * Register for push notifications and get Expo Push Token
 * @returns {Promise<string|null>} Expo push token or null if failed
 */
export const registerForPushNotifications = async () => {
  try {
    // Not available on web
    if (!Notifications || !Device) {
      console.log('⚠️  Push notifications not available on web');
      return null;
    }

    // Check if running on physical device
    if (!Device.isDevice) {
      console.log('⚠️  Push notifications only work on physical devices');
      return null;
    }

    // Check existing permissions
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    // Request permission if not granted
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    // Permission denied
    if (finalStatus !== 'granted') {
      console.log('❌ Push notification permission denied');
      return null;
    }

    // Get Expo Push Token
    const tokenData = await Notifications.getExpoPushTokenAsync({
      projectId: Constants.expoConfig?.extra?.eas?.projectId,
    });

    const token = tokenData.data;
    console.log('📲 Expo Push Token:', token);

    // Save token locally
    await savePushToken(token);

    // Configure Android-specific notification channel
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'InstaGuard Alerts',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
        sound: 'default',
        enableVibrate: true,
        showBadge: true,
      });

      // Create additional channels for different alert types
      await Notifications.setNotificationChannelAsync('critical-alerts', {
        name: 'Critical Security Alerts',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 500, 250, 500],
        lightColor: '#FF0000',
        sound: 'default',
        enableVibrate: true,
        showBadge: true,
      });
    }

    return token;
  } catch (error) {
    console.error('Error registering for push notifications:', error);
    return null;
  }
};

/**
 * Send push token to backend for user device registration
 * @param {Function} apiCall - API function to send token to backend
 * @param {string} token - Push notification token
 * @returns {Promise<boolean>} Success status
 */
export const sendPushTokenToBackend = async (apiCall, token) => {
  try {
    if (!token) {
      console.log('⚠️  No push token available to send');
      return false;
    }

    // Send token to backend
    await apiCall('/users/push-token', {
      method: 'POST',
      data: {
        pushToken: token,
        platform: Platform.OS,
        deviceId: Constants.deviceId,
      },
    });

    console.log('✅ Push token sent to backend successfully');
    return true;
  } catch (error) {
    console.error('Error sending push token to backend:', error);
    return false;
  }
};

/**
 * Handle notification received while app is in foreground
 * @param {Function} callback - Callback function to handle notification
 * @returns {Subscription} Notification subscription
 */
export const addNotificationReceivedListener = (callback) => {
  return Notifications.addNotificationReceivedListener(callback);
};

/**
 * Handle notification tap/click
 * @param {Function} callback - Callback function to handle notification response
 * @returns {Subscription} Notification response subscription
 */
export const addNotificationResponseListener = (callback) => {
  return Notifications.addNotificationResponseReceivedListener(callback);
};

/**
 * Schedule a local notification (for testing or reminders)
 * @param {string} title - Notification title
 * @param {string} body - Notification body
 * @param {Object} data - Additional data
 * @param {number} seconds - Seconds from now to trigger notification
 * @returns {Promise<string>} Notification ID
 */
export const scheduleLocalNotification = async (title, body, data = {}, seconds = 1) => {
  try {
    const id = await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body,
        data,
        sound: 'default',
        priority: Notifications.AndroidNotificationPriority.HIGH,
      },
      trigger: {
        seconds,
      },
    });

    console.log(`📬 Local notification scheduled with ID: ${id}`);
    return id;
  } catch (error) {
    console.error('Error scheduling local notification:', error);
    throw error;
  }
};

/**
 * Cancel a scheduled notification
 * @param {string} notificationId - ID of notification to cancel
 * @returns {Promise<void>}
 */
export const cancelNotification = async (notificationId) => {
  try {
    await Notifications.cancelScheduledNotificationAsync(notificationId);
    console.log(`🗑️  Notification ${notificationId} canceled`);
  } catch (error) {
    console.error('Error canceling notification:', error);
  }
};

/**
 * Cancel all scheduled notifications
 * @returns {Promise<void>}
 */
export const cancelAllNotifications = async () => {
  try {
    await Notifications.cancelAllScheduledNotificationsAsync();
    console.log('🗑️  All notifications canceled');
  } catch (error) {
    console.error('Error canceling all notifications:', error);
  }
};

/**
 * Get notification permissions status
 * @returns {Promise<Object>} Permission status
 */
export const getNotificationPermissions = async () => {
  try {
    const { status } = await Notifications.getPermissionsAsync();
    return {
      granted: status === 'granted',
      status,
    };
  } catch (error) {
    console.error('Error getting notification permissions:', error);
    return { granted: false, status: 'undetermined' };
  }
};

/**
 * Set notification badge count (iOS)
 * @param {number} count - Badge count
 * @returns {Promise<void>}
 */
export const setBadgeCount = async (count) => {
  try {
    if (Platform.OS === 'ios') {
      await Notifications.setBadgeCountAsync(count);
    }
  } catch (error) {
    console.error('Error setting badge count:', error);
  }
};

/**
 * Clear notification badge (iOS)
 * @returns {Promise<void>}
 */
export const clearBadge = async () => {
  try {
    if (Platform.OS === 'ios') {
      await Notifications.setBadgeCountAsync(0);
    }
  } catch (error) {
    console.error('Error clearing badge:', error);
  }
};

export default {
  registerForPushNotifications,
  sendPushTokenToBackend,
  addNotificationReceivedListener,
  addNotificationResponseListener,
  scheduleLocalNotification,
  cancelNotification,
  cancelAllNotifications,
  getNotificationPermissions,
  setBadgeCount,
  clearBadge,
};
