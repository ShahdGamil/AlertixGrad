import 'dart:convert';

import 'package:hive_flutter/hive_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../models/models.dart';
import '../constants/app_constants.dart';

class LocalStorageService {
  static late SharedPreferences _prefs;
  static Box<Map>? _alertsBox;
  static Box<Map>? _snapshotsBox;
  static Box<Map>? _camerasBox;

  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    await _initHiveBoxes();
  }

  static Future<void> _initHiveBoxes() async {
    _alertsBox = await Hive.openBox<Map>(AppConstants.alertsBoxKey);
    _snapshotsBox = await Hive.openBox<Map>(AppConstants.snapshotsBoxKey);
    _camerasBox = await Hive.openBox<Map>(AppConstants.camerasBoxKey);
  }

  // Auth Token
  static Future<void> saveAuthToken(String token) async {
    await _prefs.setString(AppConstants.authTokenKey, token);
  }

  static String? getAuthToken() {
    return _prefs.getString(AppConstants.authTokenKey);
  }

  static Future<void> removeAuthToken() async {
    await _prefs.remove(AppConstants.authTokenKey);
  }

  // User Data
  static Future<void> saveUserData(UserModel user) async {
    await _prefs.setString(AppConstants.userDataKey, jsonEncode(user.toJson()));
  }

  static UserModel? getUserData() {
    final userData = _prefs.getString(AppConstants.userDataKey);
    if (userData != null) {
      return UserModel.fromJson(jsonDecode(userData));
    }
    return null;
  }

  static Future<void> removeUserData() async {
    await _prefs.remove(AppConstants.userDataKey);
  }

  // Theme Mode
  static Future<void> saveThemeMode(String mode) async {
    await _prefs.setString(AppConstants.themeKey, mode);
  }

  static String getThemeMode() {
    return _prefs.getString(AppConstants.themeKey) ?? 'system';
  }

  // Alerts Cache
  static Future<void> saveAlert(AlertModel alert) async {
    await _alertsBox?.put(alert.id, alert.toJson());
  }

  static Future<void> saveAlerts(List<AlertModel> alerts) async {
    for (final alert in alerts) {
      await _alertsBox?.put(alert.id, alert.toJson());
    }
  }

  static List<AlertModel> getAlerts() {
    final alerts = <AlertModel>[];
    if (_alertsBox != null) {
      for (final key in _alertsBox!.keys) {
        final data = _alertsBox!.get(key);
        if (data != null) {
          alerts.add(AlertModel.fromJson(Map<String, dynamic>.from(data)));
        }
      }
    }
    // Sort by timestamp descending
    alerts.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    return alerts;
  }

  static Future<void> deleteAlert(String alertId) async {
    await _alertsBox?.delete(alertId);
  }

  static Future<void> clearAlerts() async {
    await _alertsBox?.clear();
  }

  // Snapshots Cache
  static Future<void> saveSnapshot(SnapshotModel snapshot) async {
    await _snapshotsBox?.put(snapshot.id, snapshot.toJson());
  }

  static Future<void> saveSnapshots(List<SnapshotModel> snapshots) async {
    for (final snapshot in snapshots) {
      await _snapshotsBox?.put(snapshot.id, snapshot.toJson());
    }
  }

  static List<SnapshotModel> getSnapshots() {
    final snapshots = <SnapshotModel>[];
    if (_snapshotsBox != null) {
      for (final key in _snapshotsBox!.keys) {
        final data = _snapshotsBox!.get(key);
        if (data != null) {
          snapshots
              .add(SnapshotModel.fromJson(Map<String, dynamic>.from(data)));
        }
      }
    }
    // Sort by captured date descending
    snapshots.sort((a, b) => b.capturedAt.compareTo(a.capturedAt));
    return snapshots;
  }

  static Future<void> deleteSnapshot(String snapshotId) async {
    await _snapshotsBox?.delete(snapshotId);
  }

  static Future<void> clearSnapshots() async {
    await _snapshotsBox?.clear();
  }

  // Cameras Cache
  static Future<void> saveCamera(CameraModel camera) async {
    await _camerasBox?.put(camera.id, camera.toJson());
  }

  static Future<void> saveCameras(List<CameraModel> cameras) async {
    for (final camera in cameras) {
      await _camerasBox?.put(camera.id, camera.toJson());
    }
  }

  static List<CameraModel> getCameras() {
    final cameras = <CameraModel>[];
    if (_camerasBox != null) {
      for (final key in _camerasBox!.keys) {
        final data = _camerasBox!.get(key);
        if (data != null) {
          cameras.add(CameraModel.fromJson(Map<String, dynamic>.from(data)));
        }
      }
    }
    // Sort by created date descending
    cameras.sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return cameras;
  }

  static CameraModel? getCameraById(String cameraId) {
    final data = _camerasBox?.get(cameraId);
    if (data != null) {
      return CameraModel.fromJson(Map<String, dynamic>.from(data));
    }
    return null;
  }

  static Future<void> deleteCamera(String cameraId) async {
    await _camerasBox?.delete(cameraId);
  }

  static Future<void> clearCameras() async {
    await _camerasBox?.clear();
  }

  // Clear All Data
  static Future<void> clearAll() async {
    await _prefs.clear();
    await _alertsBox?.clear();
    await _snapshotsBox?.clear();
    await _camerasBox?.clear();
  }
}
