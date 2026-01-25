import React, { createContext, useState, useEffect, useContext } from 'react';
import { post } from '../config/api.new';
import {
  saveAuthToken,
  getAuthToken,
  deleteAuthToken,
  saveUserData,
  getUserData,
  deleteUserData,
  clearAllSecure,
} from '../utils/secureStorage';
import {
  registerForPushNotifications,
  sendPushTokenToBackend,
} from '../services/pushNotifications';
import { logEnvironmentInfo } from '../config/environment';

const AuthContext = createContext({});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    initializeAuth();
  }, []);

  /**
   * Initialize authentication on app startup
   */
  const initializeAuth = async () => {
    try {
      // Log environment info in development
      logEnvironmentInfo();

      // Check for existing auth token and user data
      const token = await getAuthToken();
      const userData = await getUserData();

      if (token && userData) {
        setUser(userData);
        setIsAuthenticated(true);

        // Register for push notifications if authenticated
        await registerPushNotifications();
      }
    } catch (error) {
      console.error('❌ Auth initialization error:', error);
      // Clear potentially corrupted data
      await clearAllSecure();
    } finally {
      setLoading(false);
    }
  };

  /**
   * Register for push notifications
   */
  const registerPushNotifications = async () => {
    try {
      const pushToken = await registerForPushNotifications();
      if (pushToken) {
        // Send token to backend (implement this endpoint in your backend)
        await sendPushTokenToBackend(post, pushToken);
      }
    } catch (error) {
      console.error('⚠️  Push notification registration error:', error);
      // Don't block login if push notifications fail
    }
  };

  /**
   * Login with email and password
   * @param {string} email
   * @param {string} password
   * @returns {Promise<Object>}
   */
  const login = async (email, password) => {
    try {
      setLoading(true);

      // Call login API
      const response = await post('/auth/login', { email, password });

      if (response.success && response.data) {
        const { user: userData, token } = response.data;

        // Save token securely
        await saveAuthToken(token);

        // Save user data
        await saveUserData(userData);

        // Update state
        setUser(userData);
        setIsAuthenticated(true);

        // Register for push notifications
        await registerPushNotifications();

        return {
          success: true,
          message: 'Login successful',
        };
      }

      return {
        success: false,
        message: response.message || 'Login failed',
      };
    } catch (error) {
      console.error('❌ Login error:', error);

      let errorMessage = 'Login failed. Please try again.';

      if (error.isNetworkError) {
        errorMessage = 'No internet connection. Please check your network.';
      } else if (error.statusCode === 401) {
        errorMessage = 'Invalid email or password.';
      } else if (error.message) {
        errorMessage = error.message;
      }

      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Register new user
   * @param {string} name
   * @param {string} email
   * @param {string} password
   * @param {string} role
   * @returns {Promise<Object>}
   */
  const register = async (name, email, password, role = 'viewer') => {
    try {
      setLoading(true);

      // Call register API
      const response = await post('/auth/register', {
        name,
        email,
        password,
        role,
      });

      if (response.success && response.data) {
        const { user: userData, token } = response.data;

        // Save token securely
        await saveAuthToken(token);

        // Save user data
        await saveUserData(userData);

        // Update state
        setUser(userData);
        setIsAuthenticated(true);

        // Register for push notifications
        await registerPushNotifications();

        return {
          success: true,
          message: 'Registration successful',
        };
      }

      return {
        success: false,
        message: response.message || 'Registration failed',
      };
    } catch (error) {
      console.error('❌ Registration error:', error);

      let errorMessage = 'Registration failed. Please try again.';

      if (error.isNetworkError) {
        errorMessage = 'No internet connection. Please check your network.';
      } else if (error.statusCode === 400) {
        errorMessage = error.message || 'Invalid registration data.';
      } else if (error.message) {
        errorMessage = error.message;
      }

      return {
        success: false,
        message: errorMessage,
        details: error.details,
      };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Logout user
   * @returns {Promise<void>}
   */
  const logout = async () => {
    try {
      setLoading(true);

      // Clear all secure storage
      await clearAllSecure();

      // Update state
      setUser(null);
      setIsAuthenticated(false);

      console.log('✅ Logout successful');
    } catch (error) {
      console.error('❌ Logout error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Update user data
   * @param {Object} userData
   * @returns {Promise<void>}
   */
  const updateUser = async (userData) => {
    try {
      // Merge with existing user data
      const updatedUser = { ...user, ...userData };

      // Save updated user data
      await saveUserData(updatedUser);

      // Update state
      setUser(updatedUser);
    } catch (error) {
      console.error('❌ Update user error:', error);
    }
  };

  /**
   * Refresh user data from backend
   * @returns {Promise<Object>}
   */
  const refreshUser = async () => {
    try {
      // Call get user profile API
      const response = await post('/auth/me');

      if (response.success && response.data) {
        const userData = response.data.user;

        // Save updated user data
        await saveUserData(userData);

        // Update state
        setUser(userData);

        return {
          success: true,
          data: userData,
        };
      }

      return {
        success: false,
        message: 'Failed to refresh user data',
      };
    } catch (error) {
      console.error('❌ Refresh user error:', error);

      // If unauthorized, logout
      if (error.requiresAuth) {
        await logout();
      }

      return {
        success: false,
        message: error.message || 'Failed to refresh user data',
      };
    }
  };

  /**
   * Check if user has specific role
   * @param {string|Array<string>} roles
   * @returns {boolean}
   */
  const hasRole = (roles) => {
    if (!user || !user.role) return false;

    if (Array.isArray(roles)) {
      return roles.includes(user.role);
    }

    return user.role === roles;
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateUser,
    refreshUser,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
