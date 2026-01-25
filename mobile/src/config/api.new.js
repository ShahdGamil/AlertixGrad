import axios from 'axios';
import axiosRetry from 'axios-retry';
import NetInfo from '@react-native-community/netinfo';
import ENV, { API_TIMEOUT, RETRY_ATTEMPTS, RETRY_DELAY, ENABLE_LOGGING } from './environment';
import { getAuthToken, deleteAuthToken, deleteUserData } from '../utils/secureStorage';

/**
 * Mobile-First API Service
 *
 * Features:
 * - Automatic retry for failed requests
 * - Network connectivity detection
 * - Request/response interceptors
 * - Bearer token authentication
 * - Mobile-optimized error handling
 * - Request timeout handling
 * - Detailed logging in development
 */

// Create axios instance with mobile-optimized configuration
const api = axios.create({
  baseURL: ENV.apiUrl,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// ===== Network Connectivity Check =====

let isConnected = true;

// Monitor network connectivity
NetInfo.addEventListener(state => {
  isConnected = state.isConnected && state.isInternetReachable;

  if (ENABLE_LOGGING) {
    console.log(`📶 Network Status: ${isConnected ? 'Connected' : 'Disconnected'}`);
  }
});

/**
 * Check if device is connected to internet
 * @returns {Promise<boolean>}
 */
export const checkNetworkConnectivity = async () => {
  try {
    const state = await NetInfo.fetch();
    isConnected = state.isConnected && state.isInternetReachable;
    return isConnected;
  } catch (error) {
    console.error('Error checking network connectivity:', error);
    return false;
  }
};

// ===== Axios Retry Configuration =====

axiosRetry(api, {
  retries: RETRY_ATTEMPTS,
  retryDelay: (retryCount) => {
    const delay = retryCount * RETRY_DELAY;
    if (ENABLE_LOGGING) {
      console.log(`🔄 Retry attempt ${retryCount}, waiting ${delay}ms...`);
    }
    return delay;
  },
  retryCondition: (error) => {
    // Retry on network errors or 5xx server errors
    return (
      axiosRetry.isNetworkOrIdempotentRequestError(error) ||
      (error.response?.status >= 500 && error.response?.status < 600)
    );
  },
  shouldResetTimeout: true,
});

// ===== Request Interceptor =====

api.interceptors.request.use(
  async (config) => {
    // Check network connectivity before making request
    if (!isConnected) {
      return Promise.reject({
        message: 'No internet connection',
        code: 'NETWORK_ERROR',
        isNetworkError: true,
      });
    }

    // Add authentication token
    const token = await getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request timestamp for performance monitoring
    config.metadata = { startTime: Date.now() };

    // Log request in development
    if (ENABLE_LOGGING) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
      if (config.data) {
        console.log('📦 Request Data:', config.data);
      }
    }

    return config;
  },
  (error) => {
    if (ENABLE_LOGGING) {
      console.error('❌ Request Interceptor Error:', error);
    }
    return Promise.reject(error);
  }
);

// ===== Response Interceptor =====

api.interceptors.response.use(
  (response) => {
    // Calculate request duration
    const duration = Date.now() - response.config.metadata.startTime;

    // Log response in development
    if (ENABLE_LOGGING) {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`);
      console.log(`⏱️  Duration: ${duration}ms`);
      console.log('📦 Response Data:', response.data);
    }

    return response;
  },
  async (error) => {
    // Log error in development
    if (ENABLE_LOGGING) {
      console.error('❌ API Error:', error.message);
      if (error.response) {
        console.error('📦 Error Response:', error.response.data);
        console.error('🔢 Status Code:', error.response.status);
      }
    }

    // Handle network errors
    if (!error.response) {
      return Promise.reject({
        message: error.message || 'Network error occurred',
        code: 'NETWORK_ERROR',
        isNetworkError: true,
        originalError: error,
      });
    }

    // Handle authentication errors
    if (error.response.status === 401) {
      // Token expired or invalid - clear auth data
      await deleteAuthToken();
      await deleteUserData();

      // You can trigger navigation to login screen here
      // This will be handled by AuthContext
      return Promise.reject({
        message: 'Session expired. Please login again.',
        code: 'UNAUTHORIZED',
        statusCode: 401,
        requiresAuth: true,
      });
    }

    // Handle forbidden errors
    if (error.response.status === 403) {
      return Promise.reject({
        message: 'You do not have permission to perform this action',
        code: 'FORBIDDEN',
        statusCode: 403,
      });
    }

    // Handle not found errors
    if (error.response.status === 404) {
      return Promise.reject({
        message: 'The requested resource was not found',
        code: 'NOT_FOUND',
        statusCode: 404,
      });
    }

    // Handle validation errors
    if (error.response.status === 400) {
      const errorData = error.response.data?.error || error.response.data;
      return Promise.reject({
        message: errorData.message || 'Invalid request',
        code: 'VALIDATION_ERROR',
        statusCode: 400,
        details: errorData.details || [],
      });
    }

    // Handle server errors
    if (error.response.status >= 500) {
      return Promise.reject({
        message: 'Server error. Please try again later.',
        code: 'SERVER_ERROR',
        statusCode: error.response.status,
        retry: true,
        retryAfter: error.response.data?.error?.retryAfter || 5000,
      });
    }

    // Handle other errors
    return Promise.reject({
      message: error.response.data?.error?.message || error.message || 'An error occurred',
      code: error.response.data?.error?.code || 'UNKNOWN_ERROR',
      statusCode: error.response.status,
      originalError: error,
    });
  }
);

// ===== Helper Functions =====

/**
 * Make a GET request
 * @param {string} url - Endpoint URL
 * @param {Object} config - Axios config
 * @returns {Promise<any>}
 */
export const get = async (url, config = {}) => {
  try {
    const response = await api.get(url, config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Make a POST request
 * @param {string} url - Endpoint URL
 * @param {Object} data - Request body
 * @param {Object} config - Axios config
 * @returns {Promise<any>}
 */
export const post = async (url, data, config = {}) => {
  try {
    const response = await api.post(url, data, config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Make a PUT request
 * @param {string} url - Endpoint URL
 * @param {Object} data - Request body
 * @param {Object} config - Axios config
 * @returns {Promise<any>}
 */
export const put = async (url, data, config = {}) => {
  try {
    const response = await api.put(url, data, config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Make a PATCH request
 * @param {string} url - Endpoint URL
 * @param {Object} data - Request body
 * @param {Object} config - Axios config
 * @returns {Promise<any>}
 */
export const patch = async (url, data, config = {}) => {
  try {
    const response = await api.patch(url, data, config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Make a DELETE request
 * @param {string} url - Endpoint URL
 * @param {Object} config - Axios config
 * @returns {Promise<any>}
 */
export const del = async (url, config = {}) => {
  try {
    const response = await api.delete(url, config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Upload file with progress tracking
 * @param {string} url - Endpoint URL
 * @param {FormData} formData - Form data with file
 * @param {Function} onProgress - Progress callback
 * @returns {Promise<any>}
 */
export const uploadFile = async (url, formData, onProgress) => {
  try {
    const response = await api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        if (onProgress) {
          onProgress(percentCompleted);
        }
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Check API health
 * @returns {Promise<Object>}
 */
export const checkAPIHealth = async () => {
  try {
    const response = await api.get('/health', { timeout: 5000 });
    return {
      healthy: true,
      data: response.data,
    };
  } catch (error) {
    return {
      healthy: false,
      error: error.message,
    };
  }
};

// Export axios instance for advanced usage
export { api };

// Export default instance
export default api;
