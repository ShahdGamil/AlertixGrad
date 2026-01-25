import { Platform } from 'react-native';

// Web-compatible: Only import Constants on native platforms
let Constants = null;
if (Platform.OS !== 'web') {
  try {
    Constants = require('expo-constants').default;
  } catch (e) {
    console.warn('expo-constants not available');
  }
}

/**
 * Environment Configuration for Mobile App
 *
 * This file manages API base URLs for different environments and platforms:
 * - Development: Local backend server
 * - Staging: Staging server
 * - Production: Production server
 *
 * Platform-specific handling:
 * - Android Emulator: Uses 10.0.2.2 to access host machine's localhost
 * - iOS Simulator: Uses localhost
 * - Physical Devices: Uses local network IP address
 * - Web: Uses localhost or local IP
 */

// Development configuration
const DEV_CONFIG = {
  // IMPORTANT: Update LOCAL_IP with your computer's IP address
  // Find it using: ipconfig (Windows) or ifconfig (Mac/Linux)
  LOCAL_IP: '192.168.100.139', // <-- Your actual WiFi IP
  PORT: '5000',
};

// Get the appropriate API base URL based on platform and environment
const getApiUrl = () => {
  const { LOCAL_IP, PORT } = DEV_CONFIG;

  // Production environment
  if (typeof __DEV__ !== 'undefined' && !__DEV__) {
    return 'https://your-production-api.com/api/v1';
  }

  // Web platform - use localhost
  if (Platform.OS === 'web') {
    return `http://localhost:${PORT}/api/v1`;
  }

  // Development environment - platform specific
  if (Platform.OS === 'android') {
    // Android Emulator: 10.0.2.2 maps to host machine's localhost
    // Physical Android Device: Use local network IP
    if (Constants) {
      try {
        const expoConfig = Constants.expoConfig || Constants.manifest2 || Constants.manifest;
        const debuggerHost = expoConfig?.hostUri || expoConfig?.debuggerHost;
        const isEmulator = debuggerHost?.includes('10.0.2.2');

        if (isEmulator) {
          return `http://10.0.2.2:${PORT}/api/v1`;
        }
      } catch (e) {
        console.warn('Could not detect emulator, using local IP');
      }
    }
    return `http://${LOCAL_IP}:${PORT}/api/v1`;
  }

  if (Platform.OS === 'ios') {
    // iOS Simulator can use localhost
    // Physical iOS Device: Use local network IP
    const isSimulator = Platform.isPad || Platform.isTVOS ? false : true;

    if (isSimulator) {
      return `http://localhost:${PORT}/api/v1`;
    }
    return `http://${LOCAL_IP}:${PORT}/api/v1`;
  }

  // Fallback
  return `http://localhost:${PORT}/api/v1`;
};

// Environment configuration object
const ENV = {
  dev: {
    apiUrl: getApiUrl(),
    timeout: 30000, // 30 seconds - longer timeout for development
    retryAttempts: 3,
    retryDelay: 1000,
    enableLogging: true,
  },
  staging: {
    apiUrl: 'https://staging-api.instaguard.com/api/v1',
    timeout: 20000,
    retryAttempts: 2,
    retryDelay: 1000,
    enableLogging: true,
  },
  prod: {
    apiUrl: 'https://api.instaguard.com/api/v1',
    timeout: 15000,
    retryAttempts: 2,
    retryDelay: 1000,
    enableLogging: false,
  },
};

// Determine current environment
const getEnvVars = () => {
  if (__DEV__) {
    return ENV.dev;
  }
  // You can add staging detection logic here if needed
  return ENV.prod;
};

export default getEnvVars();

// Export individual values for convenience
export const API_URL = getEnvVars().apiUrl;
export const API_TIMEOUT = getEnvVars().timeout;
export const RETRY_ATTEMPTS = getEnvVars().retryAttempts;
export const RETRY_DELAY = getEnvVars().retryDelay;
export const ENABLE_LOGGING = getEnvVars().enableLogging;

// Helper function to log environment info (useful for debugging)
export const logEnvironmentInfo = () => {
  if (__DEV__) {
    console.log('📱 Mobile App Environment Configuration');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(`Platform: ${Platform.OS}`);
    console.log(`API URL: ${API_URL}`);
    console.log(`Timeout: ${API_TIMEOUT}ms`);
    console.log(`Environment: ${__DEV__ ? 'Development' : 'Production'}`);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  }
};
