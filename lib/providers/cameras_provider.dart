import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import '../models/models.dart';
import '../core/services/local_storage_service.dart';

// Cameras Provider
final camerasProvider =
    StateNotifierProvider<CamerasNotifier, AsyncValue<List<CameraModel>>>((ref) {
  return CamerasNotifier();
});

class CamerasNotifier extends StateNotifier<AsyncValue<List<CameraModel>>> {
  CamerasNotifier() : super(const AsyncValue.loading()) {
    _loadCameras();
  }

  final _uuid = const Uuid();

  Future<void> _loadCameras() async {
    try {
      final cameras = LocalStorageService.getCameras();
      state = AsyncValue.data(cameras);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    await _loadCameras();
  }

  Future<void> addCamera({
    required String name,
    required String location,
    String? cameraNumber,
  }) async {
    try {
      final camera = CameraModel(
        id: _uuid.v4(),
        name: name,
        location: location,
        cameraNumber: cameraNumber,
        createdAt: DateTime.now(),
        isActive: true,
      );

      await LocalStorageService.saveCamera(camera);
      await _loadCameras();
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  Future<void> updateCamera(CameraModel camera) async {
    try {
      await LocalStorageService.saveCamera(camera);
      await _loadCameras();
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  Future<void> deleteCamera(String cameraId) async {
    try {
      await LocalStorageService.deleteCamera(cameraId);
      await _loadCameras();
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  Future<void> toggleCameraActive(String cameraId) async {
    try {
      final camera = LocalStorageService.getCameraById(cameraId);
      if (camera != null) {
        final updated = camera.copyWith(isActive: !camera.isActive);
        await LocalStorageService.saveCamera(updated);
        await _loadCameras();
      }
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  Future<void> clearAll() async {
    try {
      await LocalStorageService.clearCameras();
      await _loadCameras();
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
}

// Selected Camera Provider (for image upload)
final selectedCameraProvider = StateProvider<CameraModel?>((ref) => null);
