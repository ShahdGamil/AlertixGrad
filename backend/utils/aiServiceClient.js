import axios from 'axios';
import FormData from 'form-data';

/**
 * AI Service Client
 * Handles all HTTP communication with the AI inference service
 */
class AIServiceClient {
  constructor() {
    this.baseURL = process.env.AI_SERVICE_URL || 'http://localhost:5001';
    this.apiKey = process.env.AI_SERVICE_API_KEY || 'your-secret-api-key-change-in-production';
    this.timeout = 30000; // 30 seconds default timeout

    // Create axios instance with default configuration
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: this.timeout,
      headers: {
        'X-API-Key': this.apiKey
      }
    });

    // Add retry interceptor for failed requests
    this.client.interceptors.response.use(
      response => response,
      async error => {
        const { config, response } = error;

        // Retry on 503 (service unavailable) or network errors
        if (!config._retry && (!response || response.status === 503)) {
          config._retry = true;

          // Wait 1 second before retry
          await new Promise(resolve => setTimeout(resolve, 1000));

          return this.client(config);
        }

        throw error;
      }
    );
  }

  /**
   * Detect threats in an image
   * @param {Buffer} imageBuffer - Image data as buffer
   * @param {Object} options - Detection options
   * @param {string} options.camera_id - Camera identifier
   * @param {number} options.conf_threshold - Confidence threshold (0-1)
   * @param {number} options.iou_threshold - IOU threshold (0-1)
   * @returns {Promise<Object>} Detection results
   */
  async detectImage(imageBuffer, options = {}) {
    try {
      const formData = new FormData();
      formData.append('image', imageBuffer, { filename: 'image.jpg' });

      if (options.camera_id) {
        formData.append('camera_id', options.camera_id);
      }
      if (options.conf_threshold !== undefined) {
        formData.append('conf_threshold', options.conf_threshold);
      }
      if (options.iou_threshold !== undefined) {
        formData.append('iou_threshold', options.iou_threshold);
      }

      const response = await this.client.post('/api/v1/detect/image', formData, {
        headers: formData.getHeaders()
      });

      return response.data;
    } catch (error) {
      this._handleError('detectImage', error);
    }
  }

  /**
   * Start stream processing
   * @param {string} streamUrl - RTSP/HTTP stream URL
   * @param {string} cameraId - Camera identifier
   * @param {Object} options - Stream options
   * @param {number} options.duration - Processing duration in seconds
   * @param {number} options.frame_skip - Process every Nth frame
   * @param {string} options.callback_url - Webhook URL for detections
   * @returns {Promise<Object>} Stream task information
   */
  async startStream(streamUrl, cameraId, options = {}) {
    try {
      const response = await this.client.post('/api/v1/detect/stream', {
        stream_url: streamUrl,
        camera_id: cameraId,
        duration: options.duration || 300,
        frame_skip: options.frame_skip || 5,
        callback_url: options.callback_url
      });

      return response.data;
    } catch (error) {
      this._handleError('startStream', error);
    }
  }

  /**
   * Get stream processing status
   * @param {string} taskId - Stream task ID
   * @returns {Promise<Object>} Stream status
   */
  async getStreamStatus(taskId) {
    try {
      const response = await this.client.get(`/api/v1/stream/status/${taskId}`);
      return response.data;
    } catch (error) {
      this._handleError('getStreamStatus', error);
    }
  }

  /**
   * Stop stream processing
   * @param {string} taskId - Stream task ID
   * @returns {Promise<Object>} Stop confirmation
   */
  async stopStream(taskId) {
    try {
      const response = await this.client.post(`/api/v1/stream/stop/${taskId}`);
      return response.data;
    } catch (error) {
      this._handleError('stopStream', error);
    }
  }

  /**
   * Health check
   * @returns {Promise<Object>} Health status
   */
  async healthCheck() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      this._handleError('healthCheck', error);
    }
  }

  /**
   * Get detailed AI service status
   * @returns {Promise<Object>} Service status including models, device, etc.
   */
  async getStatus() {
    try {
      const response = await this.client.get('/api/v1/status');
      return response.data;
    } catch (error) {
      this._handleError('getStatus', error);
    }
  }

  /**
   * Handle errors with context
   * @private
   */
  _handleError(method, error) {
    const errorMessage = error.response?.data?.message || error.message || 'Unknown error';
    const statusCode = error.response?.status;

    const enhancedError = new Error(`AI Service Error (${method}): ${errorMessage}`);
    enhancedError.statusCode = statusCode;
    enhancedError.originalError = error;
    enhancedError.isAIServiceError = true;

    throw enhancedError;
  }
}

// Export singleton instance
export default new AIServiceClient();
