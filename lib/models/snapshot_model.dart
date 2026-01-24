class SnapshotModel {
  SnapshotModel({
    required this.id,
    required this.imageUrl,
    this.localPath,
    required this.capturedAt,
    this.cameraId,
    this.fileSize,
    this.resolution,
    this.hasDetection = false,
  });

  factory SnapshotModel.fromJson(Map<String, dynamic> json) {
    return SnapshotModel(
      id: json['id'] as String,
      imageUrl:
          json['image_url'] as String? ?? json['imageUrl'] as String? ?? '',
      localPath: json['local_path'] as String? ?? json['localPath'] as String?,
      capturedAt: json['captured_at'] != null
          ? DateTime.parse(json['captured_at'] as String)
          : json['capturedAt'] != null
              ? DateTime.parse(json['capturedAt'] as String)
              : DateTime.now(),
      cameraId: json['camera_id'] as String? ?? json['cameraId'] as String?,
      fileSize: json['file_size'] as int? ?? json['fileSize'] as int?,
      resolution: json['resolution'] as String?,
      hasDetection: json['has_detection'] as bool? ??
          json['hasDetection'] as bool? ??
          false,
    );
  }
  final String id;
  final String imageUrl;
  final String? localPath;
  final DateTime capturedAt;
  final String? cameraId;
  final int? fileSize;
  final String? resolution;
  final bool hasDetection;

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'image_url': imageUrl,
      'local_path': localPath,
      'captured_at': capturedAt.toIso8601String(),
      'camera_id': cameraId,
      'file_size': fileSize,
      'resolution': resolution,
      'has_detection': hasDetection,
    };
  }

  SnapshotModel copyWith({
    String? id,
    String? imageUrl,
    String? localPath,
    DateTime? capturedAt,
    String? cameraId,
    int? fileSize,
    String? resolution,
    bool? hasDetection,
  }) {
    return SnapshotModel(
      id: id ?? this.id,
      imageUrl: imageUrl ?? this.imageUrl,
      localPath: localPath ?? this.localPath,
      capturedAt: capturedAt ?? this.capturedAt,
      cameraId: cameraId ?? this.cameraId,
      fileSize: fileSize ?? this.fileSize,
      resolution: resolution ?? this.resolution,
      hasDetection: hasDetection ?? this.hasDetection,
    );
  }

  String get formattedFileSize {
    if (fileSize == null) return 'Unknown';
    if (fileSize! < 1024) return '${fileSize}B';
    if (fileSize! < 1024 * 1024)
      return '${(fileSize! / 1024).toStringAsFixed(1)}KB';
    return '${(fileSize! / (1024 * 1024)).toStringAsFixed(1)}MB';
  }
}
