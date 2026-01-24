import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/camera_service.dart';
import '../models/models.dart';
import '../core/constants/app_constants.dart';

// Camera Service Provider
final cameraServiceProvider = Provider<CameraService>((ref) => CameraService());

// Camera Status Provider
final cameraStatusProvider =
    StateNotifierProvider<CameraStatusNotifier, CameraStatus>((ref) {
  final cameraService = ref.watch(cameraServiceProvider);
  return CameraStatusNotifier(cameraService);
});

class CameraStatusNotifier extends StateNotifier<CameraStatus> {
  CameraStatusNotifier(this._cameraService) : super(CameraStatus.connecting()) {
    _fetchStatus();
    _startPeriodicCheck();
  }
  final CameraService _cameraService;
  Timer? _statusTimer;

  void _startPeriodicCheck() {
    _statusTimer?.cancel();
    _statusTimer = Timer.periodic(
      AppConstants.cameraStatusCheckInterval,
      (_) => _fetchStatus(),
    );
  }

  Future<void> _fetchStatus() async {
    try {
      final status = await _cameraService.getCameraStatus();
      state = status;
    } catch (e) {
      state = CameraStatus.offline();
    }
  }

  Future<void> refresh() async {
    state = CameraStatus.connecting();
    await _fetchStatus();
  }

  @override
  void dispose() {
    _statusTimer?.cancel();
    super.dispose();
  }
}

// Latest Snapshot Provider
final latestSnapshotProvider =
    StateNotifierProvider<LatestSnapshotNotifier, AsyncValue<SnapshotModel?>>(
        (ref) {
  final cameraService = ref.watch(cameraServiceProvider);
  return LatestSnapshotNotifier(cameraService);
});

class LatestSnapshotNotifier extends StateNotifier<AsyncValue<SnapshotModel?>> {
  LatestSnapshotNotifier(this._cameraService)
      : super(const AsyncValue.loading()) {
    _fetchSnapshot();
    _startAutoRefresh();
  }
  final CameraService _cameraService;
  Timer? _refreshTimer;
  bool _isDisposed = false;

  void _startAutoRefresh() {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(
      AppConstants.snapshotRefreshInterval,
      (_) => _fetchSnapshot(),
    );
  }

  Future<void> _fetchSnapshot() async {
    if (_isDisposed) return;

    try {
      final snapshot = await _cameraService.getLatestSnapshot();
      if (!_isDisposed) {
        state = AsyncValue.data(snapshot);
      }
    } catch (e, st) {
      if (!_isDisposed) {
        state = AsyncValue.error(e, st);
      }
    }
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    await _fetchSnapshot();
  }

  void pauseAutoRefresh() {
    _refreshTimer?.cancel();
  }

  void resumeAutoRefresh() {
    _startAutoRefresh();
  }

  @override
  void dispose() {
    _isDisposed = true;
    _refreshTimer?.cancel();
    super.dispose();
  }
}

// All Snapshots Provider
final allSnapshotsProvider = StateNotifierProvider<AllSnapshotsNotifier,
    AsyncValue<List<SnapshotModel>>>((ref) {
  final cameraService = ref.watch(cameraServiceProvider);
  return AllSnapshotsNotifier(cameraService);
});

class AllSnapshotsNotifier
    extends StateNotifier<AsyncValue<List<SnapshotModel>>> {
  AllSnapshotsNotifier(this._cameraService)
      : super(const AsyncValue.loading()) {
    fetchSnapshots();
  }
  final CameraService _cameraService;
  int _currentPage = 1;
  bool _hasMore = true;

  Future<void> fetchSnapshots() async {
    try {
      _currentPage = 1;
      _hasMore = true;
      final snapshots =
          await _cameraService.getAllSnapshots(page: _currentPage);
      state = AsyncValue.data(snapshots);
      _hasMore = snapshots.length >= 20;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> loadMore() async {
    if (!_hasMore) return;

    final currentSnapshots = state.valueOrNull ?? [];

    try {
      _currentPage++;
      final newSnapshots =
          await _cameraService.getAllSnapshots(page: _currentPage);
      state = AsyncValue.data([...currentSnapshots, ...newSnapshots]);
      _hasMore = newSnapshots.length >= 20;
    } catch (e) {
      _currentPage--;
    }
  }

  Future<void> deleteSnapshot(String id) async {
    final deleted = await _cameraService.deleteSnapshot(id);
    if (deleted) {
      final currentSnapshots = state.valueOrNull ?? [];
      state = AsyncValue.data(
        currentSnapshots.where((s) => s.id != id).toList(),
      );
    }
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    await fetchSnapshots();
  }
}
