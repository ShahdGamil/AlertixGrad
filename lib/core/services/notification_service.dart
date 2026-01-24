import 'dart:convert';
// import 'package:firebase_messaging/firebase_messaging.dart';  // Disabled - Firebase not in use
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../constants/app_constants.dart';

class NotificationService {
  // static final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  static final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  static String? _fcmToken;
  static String? get fcmToken => _fcmToken;

  static Future<void> init() async {
    // Request permission - Mock implementation
    // await _requestPermission();

    // Initialize local notifications
    await _initLocalNotifications();

    // Mock FCM token
    _fcmToken = 'mock_fcm_token_${DateTime.now().millisecondsSinceEpoch}';

    // Firebase Messaging listeners disabled - not available without Firebase
  }

  // _requestPermission removed - Firebase Messaging not available

  static Future<void> _initLocalNotifications() async {
    const androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestBadgePermission: true,
      requestCriticalPermission: true,
    );

    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTap,
    );

    // Create notification channel for Android
    const androidChannel = AndroidNotificationChannel(
      AppConstants.alertChannelId,
      AppConstants.alertChannelName,
      description: AppConstants.alertChannelDescription,
      importance: Importance.max,
    );

    await _localNotifications
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(androidChannel);
  }

  // Firebase message handlers removed - Firebase Messaging not available

  static void _onNotificationTap(NotificationResponse response) {
    if (response.payload != null) {
      final data = jsonDecode(response.payload!);
      if (data['type'] == 'theft_alert') {
        // Navigate to alert details
      }
    }
  }

  static Future<void> showLocalNotification({
    required String title,
    required String body,
    String? payload,
    String? imageUrl,
  }) async {
    BigPictureStyleInformation? bigPictureStyle;

    // Android notification details
    final androidDetails = AndroidNotificationDetails(
      AppConstants.alertChannelId,
      AppConstants.alertChannelName,
      channelDescription: AppConstants.alertChannelDescription,
      importance: Importance.max,
      priority: Priority.high,
      styleInformation: bigPictureStyle,
      fullScreenIntent: true,
      category: AndroidNotificationCategory.alarm,
    );

    // iOS notification details
    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
      interruptionLevel: InterruptionLevel.critical,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _localNotifications.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      body,
      details,
      payload: payload,
    );
  }

  static Future<void> showTheftAlertNotification({
    required String alertId,
    required DateTime timestamp,
    String? imageUrl,
  }) async {
    await showLocalNotification(
      title: '🚨 Theft Detected!',
      body:
          'Suspicious activity detected at ${_formatTime(timestamp)}. Tap to view details.',
      payload: jsonEncode({
        'type': 'theft_alert',
        'alert_id': alertId,
      }),
      imageUrl: imageUrl,
    );
  }

  static String _formatTime(DateTime time) {
    final hour = time.hour.toString().padLeft(2, '0');
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }

  static Future<void> cancelAllNotifications() async {
    await _localNotifications.cancelAll();
  }

  static Future<void> cancelNotification(int id) async {
    await _localNotifications.cancel(id);
  }
}
