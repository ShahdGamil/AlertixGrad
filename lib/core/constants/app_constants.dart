class AppConstants {
  AppConstants._();

  // App Info
  static const String appName = 'Alertix';
  static const String appVersion = '1.0.0';

  // API Configuration
  static const String baseUrl = 'http://192.168.1.100:5000/api';
  static const Duration apiTimeout = Duration(seconds: 30);

  // Camera Configuration
  static const Duration snapshotRefreshInterval = Duration(seconds: 3);
  static const Duration cameraStatusCheckInterval = Duration(seconds: 10);

  // Storage Keys
  static const String authTokenKey = 'auth_token';
  static const String userDataKey = 'user_data';
  static const String themeKey = 'theme_mode';
  static const String alertsBoxKey = 'alerts_box';
  static const String snapshotsBoxKey = 'snapshots_box';
  static const String camerasBoxKey = 'cameras_box';

  // Firebase Collections
  static const String usersCollection = 'users';
  static const String alertsCollection = 'alerts';

  // Notification Channels
  static const String alertChannelId = 'theft_alerts';
  static const String alertChannelName = 'Theft Alerts';
  static const String alertChannelDescription = 'Notifications for theft detection alerts';
}

class ApiEndpoints {
  ApiEndpoints._();

  // Authentication
  static const String login = '/auth/login';
  static const String signup = '/auth/signup';
  static const String logout = '/auth/logout';
  static const String refreshToken = '/auth/refresh';

  // Camera
  static const String cameraSnapshot = '/camera/snapshot';
  static const String cameraStatus = '/camera/status';

  // Detection
  static const String detectionStatus = '/detection/status';
  static const String detectionHistory = '/detection/history';
  static const String detectUpload = '/detection/upload';

  // Alerts
  static const String alerts = '/alerts';
  static const String alertById = '/alerts/{id}';

  // Gallery
  static const String snapshots = '/snapshots';
  static const String snapshotById = '/snapshots/{id}';
}
