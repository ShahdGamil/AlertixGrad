import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Update this to your backend URL
// For Android Emulator: use 'http://10.0.2.2:5000/api/v1'
// For iOS Simulator: use 'http://localhost:5000/api/v1'
// For Web: use 'http://localhost:5000/api/v1'
// For Physical Device: use 'http://YOUR_COMPUTER_IP:5000/api/v1'
// To find your IP: ipconfig (Windows) or ifconfig (Mac/Linux)
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:5000/api/v1'  // Web/iOS - change to 10.0.2.2 for Android Emulator
  : 'https://your-production-api.com/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      await AsyncStorage.removeItem('token');
      await AsyncStorage.removeItem('user');
      // Navigate to login - handled by AuthContext
    }
    return Promise.reject(error);
  }
);

export default api;

