import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/detection_service.dart';
import '../services/alert_service.dart';
import '../core/services/alarm_service.dart';
import '../core/services/notification_service.dart';
import '../core/constants/app_constants.dart';
import '../models/models.dart';

// Detection Service Provider
final detectionServiceProvider =
    Provider<DetectionService>((ref) => DetectionService());

// Alarm Service Provider
final alarmServiceProvider = Provider<AlarmService>((ref) {
  final alarmService = AlarmService();
  alarmService.init();
  ref.onDispose(alarmService.dispose);
  return alarmService;
});

// Detection Result Provider
final detectionResultProvider = StateNotifierProvider<DetectionResultNotifier,
    AsyncValue<DetectionResult?>>((ref) {
  final detectionService = ref.watch(detectionServiceProvider);
  final alarmService = ref.watch(alarmServiceProvider);
  final alertService = ref.watch(alertServiceProvider);
  return DetectionResultNotifier(
      detectionService, alarmService, alertService, ref);
});

class DetectionResultNotifier
    extends StateNotifier<AsyncValue<DetectionResult?>> {
  DetectionResultNotifier(
    this._detectionService,
    this._alarmService,
    this._alertService,
    this._ref,
  ) : super(const AsyncValue.loading()) {
    _fetchDetectionStatus();
    _startPolling();
  }
  final DetectionService _detectionService;
  final AlarmService _alarmService;
  final AlertService _alertService;
  final Ref _ref;
  Timer? _pollingTimer;
  bool _isDisposed = false;
  bool _previousTheftDetected = false;

  void _startPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = Timer.periodic(
      AppConstants.snapshotRefreshInterval,
      (_) => _fetchDetectionStatus(),
    );
  }

  Future<void> _fetchDetectionStatus() async {
    if (_isDisposed) return;

    try {
      final result = await _detectionService.getDetectionStatus();

      if (!_isDisposed && result != null) {
        state = AsyncValue.data(result);

        // Handle theft detection
        if (result.theftDetected && !_previousTheftDetected) {
          await _handleTheftDetected(result);
        } else if (!result.theftDetected && _previousTheftDetected) {
          await _handleTheftCleared();
        }

        _previousTheftDetected = result.theftDetected;
      }
    } catch (e, st) {
      if (!_isDisposed) {
        state = AsyncValue.error(e, st);
      }
    }
  }

  Future<void> _handleTheftDetected(DetectionResult result) async {
    // Play alarm
    await _alarmService.playAlarm();

    // Create and save alert
    final alert = AlertModel.fromDetectionResult(result);
    await _alertService.saveAlert(alert);

    // Refresh alerts list
    _ref.invalidate(alertsProvider);

    // Show notification
    await NotificationService.showTheftAlertNotification(
      alertId: alert.id,
      timestamp: alert.timestamp,
      imageUrl: alert.imageUrl,
    );
  }

  Future<void> _handleTheftCleared() async {
    // Stop alarm when detection clears
    await _alarmService.stopAlarm();
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    await _fetchDetectionStatus();
  }

  void pausePolling() {
    _pollingTimer?.cancel();
  }

  void resumePolling() {
    _startPolling();
  }

  @override
  void dispose() {
    _isDisposed = true;
    _pollingTimer?.cancel();
    super.dispose();
  }
}

// Alert Service Provider
final alertServiceProvider = Provider<AlertService>((ref) => AlertService());

// Alerts Provider
final alertsProvider =
    StateNotifierProvider<AlertsNotifier, AsyncValue<List<AlertModel>>>((ref) {
  final alertService = ref.watch(alertServiceProvider);
  return AlertsNotifier(alertService);
});

class AlertsNotifier extends StateNotifier<AsyncValue<List<AlertModel>>> {
  AlertsNotifier(this._alertService) : super(const AsyncValue.loading()) {
    fetchAlerts();
  }
  final AlertService _alertService;
  int _currentPage = 1;
  bool _hasMore = true;

  Future<void> fetchAlerts() async {
    try {
      _currentPage = 1;
      _hasMore = true;

      // Cleanup invalid alerts on startup
      await _alertService.cleanupInvalidAlerts();

      // First try to get from cache
      final cached = _alertService.getCachedAlerts();
      if (cached.isNotEmpty) {
        state = AsyncValue.data(cached);
      }

      // Then fetch from server
      final alerts = await _alertService.getAlerts(page: _currentPage);

      if (alerts.isEmpty && cached.isEmpty) {
        // Generate mock data for testing
        final mockAlerts = _alertService.generateMockAlerts();
        for (final alert in mockAlerts) {
          await _alertService.saveAlert(alert);
        }
        state = AsyncValue.data(mockAlerts);
      } else {
        state = AsyncValue.data(alerts.isEmpty ? cached : alerts);
      }

      _hasMore = alerts.length >= 20;
    } catch (e, st) {
      final cached = _alertService.getCachedAlerts();
      if (cached.isNotEmpty) {
        state = AsyncValue.data(cached);
      } else {
        state = AsyncValue.error(e, st);
      }
    }
  }

  Future<void> loadMore() async {
    if (!_hasMore) return;

    final currentAlerts = state.valueOrNull ?? [];

    try {
      _currentPage++;
      final newAlerts = await _alertService.getAlerts(page: _currentPage);
      state = AsyncValue.data([...currentAlerts, ...newAlerts]);
      _hasMore = newAlerts.length >= 20;
    } catch (e) {
      _currentPage--;
    }
  }

  Future<void> deleteAlert(String id) async {
    final deleted = await _alertService.deleteAlert(id);
    if (deleted) {
      final currentAlerts = state.valueOrNull ?? [];
      state = AsyncValue.data(
        currentAlerts.where((a) => a.id != id).toList(),
      );
    }
  }

  Future<void> updateStatus(String id, AlertStatus status) async {
    await _alertService.updateAlertStatus(id, status);
    final currentAlerts = state.valueOrNull ?? [];
    state = AsyncValue.data(
      currentAlerts.map((a) {
        if (a.id == id) {
          return a.copyWith(status: status);
        }
        return a;
      }).toList(),
    );
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    await fetchAlerts();
  }

  Future<void> clearAll() async {
    await _alertService.clearAllAlerts();
    state = const AsyncValue.data([]);
  }
}

// Alarm State Provider
final alarmStateProvider =
    StateNotifierProvider<AlarmStateNotifier, AlarmState>((ref) {
  final alarmService = ref.watch(alarmServiceProvider);
  return AlarmStateNotifier(alarmService);
});

class AlarmState {
  AlarmState({this.isPlaying = false, this.isMuted = false});
  final bool isPlaying;
  final bool isMuted;

  AlarmState copyWith({bool? isPlaying, bool? isMuted}) {
    return AlarmState(
      isPlaying: isPlaying ?? this.isPlaying,
      isMuted: isMuted ?? this.isMuted,
    );
  }
}

class AlarmStateNotifier extends StateNotifier<AlarmState> {
  AlarmStateNotifier(this._alarmService) : super(AlarmState());
  final AlarmService _alarmService;

  void toggleMute() {
    _alarmService.toggleMute();
    state = state.copyWith(isMuted: _alarmService.isMuted);
  }

  void mute() {
    _alarmService.mute();
    state = state.copyWith(isPlaying: false, isMuted: true);
  }

  void unmute() {
    _alarmService.unmute();
    state = state.copyWith(isMuted: false);
  }

  void updatePlayingState(bool isPlaying) {
    state = state.copyWith(isPlaying: isPlaying);
  }
}
