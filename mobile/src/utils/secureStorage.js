import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Web-compatible: Only import SecureStore on native platforms
let SecureStore = null;
if (Platform.OS !== 'web') {
  try {
    SecureStore = require('expo-secure-store');
  } catch (e) {
    console.warn('SecureStore not available, using AsyncStorage fallback');
  }
}

/**
 * Secure Storage Utility for Mobile App
 *
 * This utility provides secure storage for sensitive data like JWT tokens.
 *
 * Platform differences:
 * - iOS: Uses Keychain Services (highly secure)
 * - Android: Uses EncryptedSharedPreferences (hardware-backed if available)
 * - Web: Falls back to AsyncStorage (less secure, but functional for dev)
 *
 * IMPORTANT: Never store sensitive data in AsyncStorage in production for iOS/Android.
 * Always use SecureStore for tokens and credentials.
 */

const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  DEVICE_ID: 'device_id',
  PUSH_TOKEN: 'push_token',
};

/**
 * Save data securely
 * @param {string} key - Storage key
 * @param {string} value - Value to store
 * @returns {Promise<void>}
 */
export const saveSecure = async (key, value) => {
  try {
    if (Platform.OS === 'web') {
      // Fallback to AsyncStorage for web
      await AsyncStorage.setItem(key, value);
      return;
    }

    // Use SecureStore for iOS and Android
    await SecureStore.setItemAsync(key, value);
  } catch (error) {
    console.error(`Error saving ${key} to secure storage:`, error);
    throw new Error(`Failed to save ${key} securely`);
  }
};

/**
 * Retrieve data securely
 * @param {string} key - Storage key
 * @returns {Promise<string|null>}
 */
export const getSecure = async (key) => {
  try {
    if (Platform.OS === 'web') {
      // Fallback to AsyncStorage for web
      return await AsyncStorage.getItem(key);
    }

    // Use SecureStore for iOS and Android
    return await SecureStore.getItemAsync(key);
  } catch (error) {
    console.error(`Error retrieving ${key} from secure storage:`, error);
    return null;
  }
};

/**
 * Delete data securely
 * @param {string} key - Storage key
 * @returns {Promise<void>}
 */
export const deleteSecure = async (key) => {
  try {
    if (Platform.OS === 'web') {
      // Fallback to AsyncStorage for web
      await AsyncStorage.removeItem(key);
      return;
    }

    // Use SecureStore for iOS and Android
    await SecureStore.deleteItemAsync(key);
  } catch (error) {
    console.error(`Error deleting ${key} from secure storage:`, error);
  }
};

/**
 * Clear all secure storage (useful for logout)
 * @returns {Promise<void>}
 */
export const clearAllSecure = async () => {
  try {
    const keys = Object.values(STORAGE_KEYS);

    if (Platform.OS === 'web') {
      await AsyncStorage.multiRemove(keys);
      return;
    }

    // Delete all keys from SecureStore
    await Promise.all(keys.map(key => SecureStore.deleteItemAsync(key)));
  } catch (error) {
    console.error('Error clearing secure storage:', error);
  }
};

// ===== Token Management =====

/**
 * Save authentication token
 * @param {string} token - JWT token
 * @returns {Promise<void>}
 */
export const saveAuthToken = async (token) => {
  return saveSecure(STORAGE_KEYS.AUTH_TOKEN, token);
};

/**
 * Get authentication token
 * @returns {Promise<string|null>}
 */
export const getAuthToken = async () => {
  return getSecure(STORAGE_KEYS.AUTH_TOKEN);
};

/**
 * Delete authentication token
 * @returns {Promise<void>}
 */
export const deleteAuthToken = async () => {
  return deleteSecure(STORAGE_KEYS.AUTH_TOKEN);
};

/**
 * Save refresh token
 * @param {string} token - Refresh token
 * @returns {Promise<void>}
 */
export const saveRefreshToken = async (token) => {
  return saveSecure(STORAGE_KEYS.REFRESH_TOKEN, token);
};

/**
 * Get refresh token
 * @returns {Promise<string|null>}
 */
export const getRefreshToken = async () => {
  return getSecure(STORAGE_KEYS.REFRESH_TOKEN);
};

// ===== User Data Management =====

/**
 * Save user data (non-sensitive)
 * Uses AsyncStorage since user profile data is not highly sensitive
 * @param {Object} userData - User profile data
 * @returns {Promise<void>}
 */
export const saveUserData = async (userData) => {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
  } catch (error) {
    console.error('Error saving user data:', error);
  }
};

/**
 * Get user data
 * @returns {Promise<Object|null>}
 */
export const getUserData = async () => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.USER_DATA);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Error retrieving user data:', error);
    return null;
  }
};

/**
 * Delete user data
 * @returns {Promise<void>}
 */
export const deleteUserData = async () => {
  try {
    await AsyncStorage.removeItem(STORAGE_KEYS.USER_DATA);
  } catch (error) {
    console.error('Error deleting user data:', error);
  }
};

// ===== Device & Push Notification Management =====

/**
 * Save device ID
 * @param {string} deviceId - Unique device identifier
 * @returns {Promise<void>}
 */
export const saveDeviceId = async (deviceId) => {
  return saveSecure(STORAGE_KEYS.DEVICE_ID, deviceId);
};

/**
 * Get device ID
 * @returns {Promise<string|null>}
 */
export const getDeviceId = async () => {
  return getSecure(STORAGE_KEYS.DEVICE_ID);
};

/**
 * Save push notification token
 * @param {string} pushToken - Expo/FCM push token
 * @returns {Promise<void>}
 */
export const savePushToken = async (pushToken) => {
  return AsyncStorage.setItem(STORAGE_KEYS.PUSH_TOKEN, pushToken);
};

/**
 * Get push notification token
 * @returns {Promise<string|null>}
 */
export const getPushToken = async () => {
  return AsyncStorage.getItem(STORAGE_KEYS.PUSH_TOKEN);
};

// Export storage keys for reference
export { STORAGE_KEYS };

export default {
  saveSecure,
  getSecure,
  deleteSecure,
  clearAllSecure,
  saveAuthToken,
  getAuthToken,
  deleteAuthToken,
  saveRefreshToken,
  getRefreshToken,
  saveUserData,
  getUserData,
  deleteUserData,
  saveDeviceId,
  getDeviceId,
  savePushToken,
  getPushToken,
  STORAGE_KEYS,
};
