import 'dart:math';
import '../core/services/api_service.dart';
import '../core/constants/app_constants.dart';
import '../models/models.dart';

class CameraService {
  final ApiService _api = ApiService();

  // Fetch latest camera snapshot
  Future<SnapshotModel?> getLatestSnapshot() async {
    try {
      final response = await _api.get(ApiEndpoints.cameraSnapshot);

      if (response.statusCode == 200 && response.data != null) {
        return SnapshotModel.fromJson(response.data as Map<String, dynamic>);
      }
      return null;
    } catch (e) {
      // Return mock data for testing
      return _getMockSnapshot();
    }
  }

  // Get camera status
  Future<CameraStatus> getCameraStatus() async {
    try {
      final response = await _api.get(ApiEndpoints.cameraStatus);

      if (response.statusCode == 200 && response.data != null) {
        return CameraStatus.fromJson(response.data as Map<String, dynamic>);
      }
      return CameraStatus.offline();
    } catch (e) {
      // Return mock data for testing
      return _getMockCameraStatus();
    }
  }

  // Get all snapshots
  Future<List<SnapshotModel>> getAllSnapshots(
      {int page = 1, int limit = 20}) async {
    try {
      final response = await _api.get(
        ApiEndpoints.snapshots,
        queryParameters: {'page': page, 'limit': limit},
      );

      if (response.statusCode == 200 && response.data != null) {
        final List<dynamic> data = response.data['snapshots'] ?? response.data;
        return data
            .map((e) => SnapshotModel.fromJson(e as Map<String, dynamic>))
            .toList();
      }
      return [];
    } catch (e) {
      // Return mock data for testing
      return _getMockSnapshots();
    }
  }

  // Delete snapshot
  Future<bool> deleteSnapshot(String snapshotId) async {
    try {
      final response = await _api.delete(
        ApiEndpoints.snapshotById.replaceAll('{id}', snapshotId),
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // Mock data for testing
  SnapshotModel _getMockSnapshot() {
    return SnapshotModel(
      id: 'snapshot_${DateTime.now().millisecondsSinceEpoch}',
      imageUrl:
          'https://picsum.photos/seed/${DateTime.now().millisecondsSinceEpoch}/800/600',
      capturedAt: DateTime.now(),
      cameraId: 'camera_1',
      resolution: '1920x1080',
    );
  }

  CameraStatus _getMockCameraStatus() {
    return CameraStatus(
      cameraId: 'camera_1',
      status: CameraConnectionStatus.online,
      lastHeartbeat: DateTime.now(),
      ipAddress: '192.168.1.100',
      resolution: '1920x1080',
      fps: 30,
      cpuUsage: 45.5,
      memoryUsage: 62.3,
      temperature: 42,
    );
  }

  List<SnapshotModel> _getMockSnapshots() {
    final random = Random();
    return List.generate(
      20,
      (index) => SnapshotModel(
        id: 'snapshot_$index',
        imageUrl: 'https://picsum.photos/seed/$index/800/600',
        capturedAt: DateTime.now().subtract(Duration(minutes: index * 5)),
        cameraId: 'camera_1',
        resolution: '1920x1080',
        hasDetection: random.nextBool() && random.nextBool(),
      ),
    );
  }
}
