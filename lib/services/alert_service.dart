import 'dart:math';
import '../core/services/api_service.dart';
import '../core/services/local_storage_service.dart';
import '../core/constants/app_constants.dart';
import '../models/models.dart';

class AlertService {
  final ApiService _api = ApiService();

  // Get all alerts from server
  Future<List<AlertModel>> getAlerts({int page = 1, int limit = 20}) async {
    try {
      final response = await _api.get(
        ApiEndpoints.alerts,
        queryParameters: {'page': page, 'limit': limit},
      );

      if (response.statusCode == 200 && response.data != null) {
        final List<dynamic> data = response.data['alerts'] ?? response.data;
        final alerts = data
            .map((e) => AlertModel.fromJson(e as Map<String, dynamic>))
            .toList();

        // Cache alerts locally
        await LocalStorageService.saveAlerts(alerts);

        return alerts;
      }
      return [];
    } catch (e) {
      // Return cached data if server is unavailable
      return LocalStorageService.getAlerts();
    }
  }

  // Get alerts from local cache
  List<AlertModel> getCachedAlerts() {
    return LocalStorageService.getAlerts();
  }

  // Get single alert by ID
  Future<AlertModel?> getAlertById(String alertId) async {
    try {
      final response = await _api.get(
        ApiEndpoints.alertById.replaceAll('{id}', alertId),
      );

      if (response.statusCode == 200 && response.data != null) {
        return AlertModel.fromJson(response.data as Map<String, dynamic>);
      }
      return null;
    } catch (e) {
      // Check local cache
      final cachedAlerts = LocalStorageService.getAlerts();
      return cachedAlerts.firstWhere(
        (alert) => alert.id == alertId,
        orElse: () => throw Exception('Alert not found'),
      );
    }
  }

  // Save alert locally
  Future<void> saveAlert(AlertModel alert) async {
    await LocalStorageService.saveAlert(alert);
  }

  // Update alert status
  Future<bool> updateAlertStatus(String alertId, AlertStatus status) async {
    try {
      final response = await _api.patch(
        ApiEndpoints.alertById.replaceAll('{id}', alertId),
        data: {'status': status.name},
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // Delete alert
  Future<bool> deleteAlert(String alertId) async {
    try {
      final response = await _api.delete(
        ApiEndpoints.alertById.replaceAll('{id}', alertId),
      );

      if (response.statusCode == 200) {
        await LocalStorageService.deleteAlert(alertId);
        return true;
      }
      return false;
    } catch (e) {
      // Still delete locally
      await LocalStorageService.deleteAlert(alertId);
      return true;
    }
  }

  // Clear all alerts
  Future<void> clearAllAlerts() async {
    await LocalStorageService.clearAlerts();
  }

  // Cleanup invalid alerts (non-suspicious or low confidence)
  Future<void> cleanupInvalidAlerts() async {
    try {
      final cachedAlerts = LocalStorageService.getAlerts();

      // Find invalid alerts to remove
      final invalidAlertIds = <String>[];
      for (final alert in cachedAlerts) {
        // Remove if not theft detected OR confidence is below threshold
        if (!alert.theftDetected || (alert.confidence ?? 0.0) < 0.6) {
          invalidAlertIds.add(alert.id);
        }
      }

      // Delete invalid alerts
      for (final id in invalidAlertIds) {
        await LocalStorageService.deleteAlert(id);
      }
    } catch (e) {
      // Silently fail - cleanup is not critical
    }
  }

  // Generate mock alerts for testing
  List<AlertModel> generateMockAlerts() {
    final random = Random();
    final alerts = <AlertModel>[];

    for (var i = 0; i < 15; i++) {
      final timestamp = DateTime.now().subtract(
        Duration(
          hours: random.nextInt(48),
          minutes: random.nextInt(60),
        ),
      );

      final confidence = 0.65 + random.nextDouble() * 0.3;
      AlertSeverity severity;
      if (confidence >= 0.9) {
        severity = AlertSeverity.critical;
      } else if (confidence >= 0.75) {
        severity = AlertSeverity.high;
      } else {
        severity = AlertSeverity.medium;
      }

      alerts.add(
        AlertModel(
          id: 'alert_$i',
          imageUrl: 'https://picsum.photos/seed/alert$i/800/600',
          timestamp: timestamp,
          theftDetected: true,
          boundingBoxes: [
            BoundingBox(
              x: 0.2 + random.nextDouble() * 0.3,
              y: 0.2 + random.nextDouble() * 0.3,
              width: 0.15 + random.nextDouble() * 0.1,
              height: 0.2 + random.nextDouble() * 0.15,
              confidence: confidence,
              label: 'Suspicious Activity',
            ),
          ],
          confidence: confidence,
          severity: severity,
          status: i == 0
              ? AlertStatus.active
              : AlertStatus.values[random.nextInt(4)],
        ),
      );
    }

    alerts.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    return alerts;
  }
}
