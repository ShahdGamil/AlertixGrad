import 'package:audioplayers/audioplayers.dart';
import 'package:vibration/vibration.dart';

class AlarmService {
  factory AlarmService() => _instance;

  AlarmService._internal();
  static final AlarmService _instance = AlarmService._internal();

  final AudioPlayer _audioPlayer = AudioPlayer();
  bool _isPlaying = false;
  bool _isMuted = false;

  bool get isPlaying => _isPlaying;
  bool get isMuted => _isMuted;

  Future<void> init() async {
    await _audioPlayer.setReleaseMode(ReleaseMode.loop);
    await _audioPlayer.setVolume(1);
  }

  Future<void> playAlarm() async {
    if (_isMuted || _isPlaying) return;

    try {
      _isPlaying = true;

      // Play alarm sound from assets
      await _audioPlayer.play(
        AssetSource('sounds/alarm.mp3'),
        volume: 1,
      );

      // Vibrate phone
      await _startVibration();
    } catch (e) {
      _isPlaying = false;
      // Fallback: just vibrate if audio fails
      await _startVibration();
    }
  }

  Future<void> stopAlarm() async {
    _isPlaying = false;

    try {
      await _audioPlayer.stop();
      await _stopVibration();
    } catch (e) {
      // Ignore errors during stop
    }
  }

  Future<void> _startVibration() async {
    final hasVibrator = await Vibration.hasVibrator();
    if (hasVibrator ?? false) {
      // Vibrate with pattern: wait 500ms, vibrate 1000ms, wait 500ms, repeat
      Vibration.vibrate(
        pattern: [500, 1000, 500, 1000, 500, 1000],
        repeat: 0,
      );
    }
  }

  Future<void> _stopVibration() async {
    await Vibration.cancel();
  }

  void mute() {
    _isMuted = true;
    stopAlarm();
  }

  void unmute() {
    _isMuted = false;
  }

  void toggleMute() {
    if (_isMuted) {
      unmute();
    } else {
      mute();
    }
  }

  Future<void> setVolume(double volume) async {
    await _audioPlayer.setVolume(volume.clamp(0.0, 1.0));
  }

  void dispose() {
    _audioPlayer.dispose();
  }
}
