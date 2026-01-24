class BoundingBox {
  BoundingBox({
    required this.x,
    required this.y,
    required this.width,
    required this.height,
    this.confidence = 0.0,
    this.label,
  });

  factory BoundingBox.fromJson(Map<String, dynamic> json) {
    return BoundingBox(
      x: (json['x'] as num).toDouble(),
      y: (json['y'] as num).toDouble(),
      width: (json['width'] as num).toDouble(),
      height: (json['height'] as num).toDouble(),
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      label: json['label'] as String?,
    );
  }
  final double x;
  final double y;
  final double width;
  final double height;
  final double confidence;
  final String? label;

  Map<String, dynamic> toJson() {
    return {
      'x': x,
      'y': y,
      'width': width,
      'height': height,
      'confidence': confidence,
      'label': label,
    };
  }

  // Convert normalized coordinates to pixel coordinates
  BoundingBox toPixelCoordinates(double imageWidth, double imageHeight) {
    return BoundingBox(
      x: x * imageWidth,
      y: y * imageHeight,
      width: width * imageWidth,
      height: height * imageHeight,
      confidence: confidence,
      label: label,
    );
  }
}

class DetectionResult {
  DetectionResult({
    required this.id,
    required this.theftDetected,
    required this.boundingBoxes,
    required this.imageUrl,
    required this.timestamp,
    this.overallConfidence,
    this.description,
  });

  factory DetectionResult.fromJson(Map<String, dynamic> json) {
    return DetectionResult(
      id: json['id'] as String? ?? '',
      theftDetected: json['theft_detected'] as bool? ?? false,
      boundingBoxes: json['bounding_box'] != null
          ? (json['bounding_box'] is List
              ? (json['bounding_box'] as List)
                  .map((e) => BoundingBox.fromJson(e as Map<String, dynamic>))
                  .toList()
              : [
                  BoundingBox.fromJson(
                      json['bounding_box'] as Map<String, dynamic>)
                ])
          : [],
      imageUrl: json['image_url'] as String? ?? '',
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.now(),
      overallConfidence: (json['confidence'] as num?)?.toDouble(),
      description: json['description'] as String?,
    );
  }
  final String id;
  final bool theftDetected;
  final List<BoundingBox> boundingBoxes;
  final String imageUrl;
  final DateTime timestamp;
  final double? overallConfidence;
  final String? description;

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'theft_detected': theftDetected,
      'bounding_box': boundingBoxes.map((e) => e.toJson()).toList(),
      'image_url': imageUrl,
      'timestamp': timestamp.toIso8601String(),
      'confidence': overallConfidence,
      'description': description,
    };
  }

  DetectionResult copyWith({
    String? id,
    bool? theftDetected,
    List<BoundingBox>? boundingBoxes,
    String? imageUrl,
    DateTime? timestamp,
    double? overallConfidence,
    String? description,
  }) {
    return DetectionResult(
      id: id ?? this.id,
      theftDetected: theftDetected ?? this.theftDetected,
      boundingBoxes: boundingBoxes ?? this.boundingBoxes,
      imageUrl: imageUrl ?? this.imageUrl,
      timestamp: timestamp ?? this.timestamp,
      overallConfidence: overallConfidence ?? this.overallConfidence,
      description: description ?? this.description,
    );
  }
}
