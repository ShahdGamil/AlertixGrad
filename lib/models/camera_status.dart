enum CameraConnectionStatus { online, offline, connecting, error }

class CameraStatus {
  CameraStatus({
    required this.cameraId,
    required this.status,
    this.lastHeartbeat,
    this.ipAddress,
    this.resolution,
    this.fps,
    this.errorMessage,
    this.cpuUsage,
    this.memoryUsage,
    this.temperature,
  });

  factory CameraStatus.fromJson(Map<String, dynamic> json) {
    return CameraStatus(
      cameraId: json['camera_id'] as String? ?? 'camera_1',
      status: CameraConnectionStatus.values.firstWhere(
        (e) => e.name == (json['status'] as String? ?? 'offline'),
        orElse: () => CameraConnectionStatus.offline,
      ),
      lastHeartbeat: json['last_heartbeat'] != null
          ? DateTime.parse(json['last_heartbeat'] as String)
          : null,
      ipAddress: json['ip_address'] as String?,
      resolution: json['resolution'] as String?,
      fps: json['fps'] as int?,
      errorMessage: json['error_message'] as String?,
      cpuUsage: (json['cpu_usage'] as num?)?.toDouble(),
      memoryUsage: (json['memory_usage'] as num?)?.toDouble(),
      temperature: (json['temperature'] as num?)?.toDouble(),
    );
  }

  factory CameraStatus.offline() {
    return CameraStatus(
      cameraId: 'camera_1',
      status: CameraConnectionStatus.offline,
    );
  }

  factory CameraStatus.connecting() {
    return CameraStatus(
      cameraId: 'camera_1',
      status: CameraConnectionStatus.connecting,
    );
  }
  final String cameraId;
  final CameraConnectionStatus status;
  final DateTime? lastHeartbeat;
  final String? ipAddress;
  final String? resolution;
  final int? fps;
  final String? errorMessage;
  final double? cpuUsage;
  final double? memoryUsage;
  final double? temperature;

  Map<String, dynamic> toJson() {
    return {
      'camera_id': cameraId,
      'status': status.name,
      'last_heartbeat': lastHeartbeat?.toIso8601String(),
      'ip_address': ipAddress,
      'resolution': resolution,
      'fps': fps,
      'error_message': errorMessage,
      'cpu_usage': cpuUsage,
      'memory_usage': memoryUsage,
      'temperature': temperature,
    };
  }

  bool get isOnline => status == CameraConnectionStatus.online;

  String get statusLabel {
    switch (status) {
      case CameraConnectionStatus.online:
        return 'Online';
      case CameraConnectionStatus.offline:
        return 'Offline';
      case CameraConnectionStatus.connecting:
        return 'Connecting...';
      case CameraConnectionStatus.error:
        return 'Error';
    }
  }

  CameraStatus copyWith({
    String? cameraId,
    CameraConnectionStatus? status,
    DateTime? lastHeartbeat,
    String? ipAddress,
    String? resolution,
    int? fps,
    String? errorMessage,
    double? cpuUsage,
    double? memoryUsage,
    double? temperature,
  }) {
    return CameraStatus(
      cameraId: cameraId ?? this.cameraId,
      status: status ?? this.status,
      lastHeartbeat: lastHeartbeat ?? this.lastHeartbeat,
      ipAddress: ipAddress ?? this.ipAddress,
      resolution: resolution ?? this.resolution,
      fps: fps ?? this.fps,
      errorMessage: errorMessage ?? this.errorMessage,
      cpuUsage: cpuUsage ?? this.cpuUsage,
      memoryUsage: memoryUsage ?? this.memoryUsage,
      temperature: temperature ?? this.temperature,
    );
  }
}
