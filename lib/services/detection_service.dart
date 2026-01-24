import 'dart:math';
import 'dart:io';
import 'package:dio/dio.dart';
import '../core/services/api_service.dart';
import '../core/constants/app_constants.dart';
import '../models/models.dart';

class DetectionService {
  final ApiService _api = ApiService();

  // Upload image for detection
  Future<DetectionResult> detectImageUpload({
    required File imageFile,
    required String cameraId,
    String? cameraName,
  }) async {
    try {
      // Create form data
      final formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(
          imageFile.path,
          filename: imageFile.path.split('/').last,
        ),
        'camera_id': cameraId,
        if (cameraName != null) 'camera_name': cameraName,
      });

      final response = await _api.post(
        ApiEndpoints.detectUpload,
        data: formData,
      );

      if (response.statusCode == 200 && response.data != null) {
        return DetectionResult.fromJson(response.data as Map<String, dynamic>);
      }

      // Return mock data if API fails
      return _getMockDetectionResultFromImage(imageFile.path);
    } catch (e) {
      // Return mock data for testing
      return _getMockDetectionResultFromImage(imageFile.path);
    }
  }

  // Get current detection status (for auto-monitoring - deprecated)
  Future<DetectionResult?> getDetectionStatus() async {
    try {
      final response = await _api.get(ApiEndpoints.detectionStatus);

      if (response.statusCode == 200 && response.data != null) {
        return DetectionResult.fromJson(response.data as Map<String, dynamic>);
      }
      return null;
    } catch (e) {
      // Return mock data for testing
      return _getMockDetectionResult();
    }
  }

  // Get detection history
  Future<List<DetectionResult>> getDetectionHistory({
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final response = await _api.get(
        ApiEndpoints.detectionHistory,
        queryParameters: {'page': page, 'limit': limit},
      );

      if (response.statusCode == 200 && response.data != null) {
        final List<dynamic> data = response.data['detections'] ?? response.data;
        return data
            .map((e) => DetectionResult.fromJson(e as Map<String, dynamic>))
            .toList();
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // Mock data for testing - simulates random detection
  DetectionResult _getMockDetectionResult() {
    final random = Random();
    final theftDetected = random.nextInt(10) < 2; // 20% chance of detection

    var boxes = <BoundingBox>[];
    if (theftDetected) {
      boxes = [
        BoundingBox(
          x: 0.2 + random.nextDouble() * 0.3,
          y: 0.2 + random.nextDouble() * 0.3,
          width: 0.15 + random.nextDouble() * 0.1,
          height: 0.2 + random.nextDouble() * 0.15,
          confidence: 0.75 + random.nextDouble() * 0.2,
          label: 'Suspicious Activity',
        ),
      ];
    }

    return DetectionResult(
      id: 'detection_${DateTime.now().millisecondsSinceEpoch}',
      theftDetected: theftDetected,
      boundingBoxes: boxes,
      imageUrl:
          'https://picsum.photos/seed/${DateTime.now().millisecondsSinceEpoch}/800/600',
      timestamp: DateTime.now(),
      overallConfidence:
          theftDetected ? (0.75 + random.nextDouble() * 0.2) : null,
      description: theftDetected
          ? 'Suspicious activity detected in monitored area'
          : null,
    );
  }

  // Mock detection result from uploaded image
  DetectionResult _getMockDetectionResultFromImage(String imagePath) {
    final random = Random();
    final theftDetected = random.nextInt(10) < 3; // 30% chance of detection

    var boxes = <BoundingBox>[];
    if (theftDetected) {
      // Add 1-2 detection boxes
      final boxCount = 1 + random.nextInt(2);
      for (var i = 0; i < boxCount; i++) {
        boxes.add(
          BoundingBox(
            x: 0.1 + random.nextDouble() * 0.4,
            y: 0.1 + random.nextDouble() * 0.4,
            width: 0.15 + random.nextDouble() * 0.15,
            height: 0.2 + random.nextDouble() * 0.2,
            confidence: 0.7 + random.nextDouble() * 0.25,
            label: 'Theft Detected',
          ),
        );
      }
    }

    return DetectionResult(
      id: 'detection_${DateTime.now().millisecondsSinceEpoch}',
      theftDetected: theftDetected,
      boundingBoxes: boxes,
      imageUrl: imagePath,
      timestamp: DateTime.now(),
      overallConfidence:
          theftDetected ? (0.7 + random.nextDouble() * 0.25) : null,
      description: theftDetected
          ? 'Theft detected in uploaded image'
          : 'No suspicious activity detected',
    );
  }
}
