import 'detection_result.dart';

enum AlertSeverity { low, medium, high, critical }

enum AlertStatus { active, acknowledged, resolved, dismissed }

class AlertModel {
  AlertModel({
    required this.id,
    required this.imageUrl,
    required this.timestamp,
    required this.theftDetected,
    this.boundingBoxes = const [],
    this.confidence,
    this.severity = AlertSeverity.high,
    this.status = AlertStatus.active,
    this.notes,
    this.acknowledgedAt,
    this.resolvedAt,
  });

  factory AlertModel.fromJson(Map<String, dynamic> json) {
    return AlertModel(
      id: json['id'] as String,
      imageUrl:
          json['image_url'] as String? ?? json['imageUrl'] as String? ?? '',
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.now(),
      theftDetected: json['theft_detected'] as bool? ??
          json['theftDetected'] as bool? ??
          false,
      boundingBoxes: json['bounding_boxes'] != null
          ? (json['bounding_boxes'] as List)
              .map((e) => BoundingBox.fromJson(e as Map<String, dynamic>))
              .toList()
          : [],
      confidence: (json['confidence'] as num?)?.toDouble(),
      severity: AlertSeverity.values.firstWhere(
        (e) => e.name == (json['severity'] as String? ?? 'high'),
        orElse: () => AlertSeverity.high,
      ),
      status: AlertStatus.values.firstWhere(
        (e) => e.name == (json['status'] as String? ?? 'active'),
        orElse: () => AlertStatus.active,
      ),
      notes: json['notes'] as String?,
      acknowledgedAt: json['acknowledged_at'] != null
          ? DateTime.parse(json['acknowledged_at'] as String)
          : null,
      resolvedAt: json['resolved_at'] != null
          ? DateTime.parse(json['resolved_at'] as String)
          : null,
    );
  }

  factory AlertModel.fromDetectionResult(DetectionResult result) {
    return AlertModel(
      id: result.id.isEmpty
          ? DateTime.now().millisecondsSinceEpoch.toString()
          : result.id,
      imageUrl: result.imageUrl,
      timestamp: result.timestamp,
      theftDetected: result.theftDetected,
      boundingBoxes: result.boundingBoxes,
      confidence: result.overallConfidence,
      severity: _calculateSeverity(result.overallConfidence),
      status: AlertStatus.active,
    );
  }
  final String id;
  final String imageUrl;
  final DateTime timestamp;
  final bool theftDetected;
  final List<BoundingBox> boundingBoxes;
  final double? confidence;
  final AlertSeverity severity;
  final AlertStatus status;
  final String? notes;
  final DateTime? acknowledgedAt;
  final DateTime? resolvedAt;

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'image_url': imageUrl,
      'timestamp': timestamp.toIso8601String(),
      'theft_detected': theftDetected,
      'bounding_boxes': boundingBoxes.map((e) => e.toJson()).toList(),
      'confidence': confidence,
      'severity': severity.name,
      'status': status.name,
      'notes': notes,
      'acknowledged_at': acknowledgedAt?.toIso8601String(),
      'resolved_at': resolvedAt?.toIso8601String(),
    };
  }

  static AlertSeverity _calculateSeverity(double? confidence) {
    if (confidence == null) return AlertSeverity.medium;
    if (confidence >= 0.9) return AlertSeverity.critical;
    if (confidence >= 0.75) return AlertSeverity.high;
    if (confidence >= 0.5) return AlertSeverity.medium;
    return AlertSeverity.low;
  }

  AlertModel copyWith({
    String? id,
    String? imageUrl,
    DateTime? timestamp,
    bool? theftDetected,
    List<BoundingBox>? boundingBoxes,
    double? confidence,
    AlertSeverity? severity,
    AlertStatus? status,
    String? notes,
    DateTime? acknowledgedAt,
    DateTime? resolvedAt,
  }) {
    return AlertModel(
      id: id ?? this.id,
      imageUrl: imageUrl ?? this.imageUrl,
      timestamp: timestamp ?? this.timestamp,
      theftDetected: theftDetected ?? this.theftDetected,
      boundingBoxes: boundingBoxes ?? this.boundingBoxes,
      confidence: confidence ?? this.confidence,
      severity: severity ?? this.severity,
      status: status ?? this.status,
      notes: notes ?? this.notes,
      acknowledgedAt: acknowledgedAt ?? this.acknowledgedAt,
      resolvedAt: resolvedAt ?? this.resolvedAt,
    );
  }

  String get severityLabel {
    switch (severity) {
      case AlertSeverity.critical:
        return 'Critical';
      case AlertSeverity.high:
        return 'High';
      case AlertSeverity.medium:
        return 'Medium';
      case AlertSeverity.low:
        return 'Low';
    }
  }

  String get statusLabel {
    switch (status) {
      case AlertStatus.active:
        return 'Active';
      case AlertStatus.acknowledged:
        return 'Acknowledged';
      case AlertStatus.resolved:
        return 'Resolved';
      case AlertStatus.dismissed:
        return 'Dismissed';
    }
  }
}
