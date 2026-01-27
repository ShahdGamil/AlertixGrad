# Flutter Integration Guide

Complete guide to integrate the YOLO backend with your Alertix Flutter app.

## 📋 Overview

The backend is already designed to work seamlessly with your existing Flutter code. The API returns JSON responses that match your `DetectionResult` model structure.

## 🔌 API Response Format

The `/predict` endpoint returns this JSON structure:

```json
{
  "theft_detected": true,
  "detections": [
    {
      "bbox": [x1, y1, x2, y2],
      "confidence": 0.87,
      "class": 0,
      "class_name": "Theft"
    }
  ],
  "total_detections": 1,
  "overall_confidence": 0.87,
  "description": "Theft detected! 1 suspicious object(s) found.",
  "camera_id": "camera_001",
  "camera_name": "Front Door Camera",
  "timestamp": "2026-01-25T10:35:00.123456",
  "confidence_threshold": 0.25,
  "image_with_boxes": "base64_encoded_image..."
}
```

## 📱 Flutter Setup

### Step 1: Update API Configuration

Edit `lib/core/constants/app_constants.dart`:

```dart
class ApiEndpoints {
  // Choose one based on your deployment:

  // Option 1: Local development (desktop)
  static const String baseUrl = 'http://localhost:8000';

  // Option 2: Android Emulator
  // static const String baseUrl = 'http://10.0.2.2:8000';

  // Option 3: iOS Simulator
  // static const String baseUrl = 'http://localhost:8000';

  // Option 4: Raspberry Pi (replace with your Pi's IP)
  // static const String baseUrl = 'http://192.168.1.100:8000';

  // Option 5: Production server
  // static const String baseUrl = 'https://your-domain.com';

  // Endpoints
  static const String detectUpload = '/predict';
  static const String health = '/health';
}
```

### Step 2: Update Detection Service

Your existing `lib/services/detection_service.dart` already works! Just verify the method signature:

```dart
Future<DetectionResult> detectImageUpload({
  required PlatformImage platformImage,
  required String cameraId,
  String? cameraName,
}) async {
  try {
    // Create form data using cross-platform approach
    final formData = FormData.fromMap({
      'image': PlatformFileUpload.fromPlatformImage(platformImage),
      'camera_id': cameraId,
      if (cameraName != null) 'camera_name': cameraName,
      'confidence_threshold': 0.25,
      'include_image': true,
    });

    final response = await _api.post(
      ApiEndpoints.detectUpload,
      data: formData,
    );

    if (response.statusCode == 200 && response.data != null) {
      return DetectionResult.fromJson(response.data as Map<String, dynamic>);
    }

    throw Exception('Detection failed');
  } catch (e) {
    logger.error('Detection error: $e');
    rethrow;
  }
}
```

### Step 3: Update Detection Result Model

Ensure your `lib/models/detection_result.dart` can parse the response:

```dart
class DetectionResult {
  final String id;
  final bool theftDetected;
  final List<BoundingBox> boundingBoxes;
  final String? imageUrl;
  final DateTime timestamp;
  final double? overallConfidence;
  final String? description;
  final String? imageWithBoxes; // Base64 encoded image

  DetectionResult({
    required this.id,
    required this.theftDetected,
    required this.boundingBoxes,
    this.imageUrl,
    required this.timestamp,
    this.overallConfidence,
    this.description,
    this.imageWithBoxes,
  });

  factory DetectionResult.fromJson(Map<String, dynamic> json) {
    // Parse detections list
    List<BoundingBox> boxes = [];
    if (json['detections'] != null) {
      boxes = (json['detections'] as List)
          .map((detection) => BoundingBox(
                x: detection['bbox'][0] / 100.0, // Normalize to 0-1
                y: detection['bbox'][1] / 100.0,
                width: (detection['bbox'][2] - detection['bbox'][0]) / 100.0,
                height: (detection['bbox'][3] - detection['bbox'][1]) / 100.0,
                confidence: detection['confidence'].toDouble(),
                label: detection['class_name'],
              ))
          .toList();
    }

    return DetectionResult(
      id: json['camera_id'] ?? 'unknown',
      theftDetected: json['theft_detected'] ?? false,
      boundingBoxes: boxes,
      imageUrl: null,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
      overallConfidence: json['overall_confidence']?.toDouble(),
      description: json['description'],
      imageWithBoxes: json['image_with_boxes'],
    );
  }
}
```

### Step 4: Display Image with Detections

Add this widget to display the base64 image with bounding boxes:

```dart
// lib/widgets/detection_image_viewer.dart

import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';

class DetectionImageViewer extends StatelessWidget {
  final String? base64Image;

  const DetectionImageViewer({
    super.key,
    this.base64Image,
  });

  @override
  Widget build(BuildContext context) {
    if (base64Image == null || base64Image!.isEmpty) {
      return Container(
        height: 200,
        color: Colors.grey[300],
        child: const Center(
          child: Text('No image available'),
        ),
      );
    }

    try {
      final Uint8List imageBytes = base64Decode(base64Image!);

      return Image.memory(
        imageBytes,
        fit: BoxFit.contain,
        errorBuilder: (context, error, stackTrace) {
          return Container(
            height: 200,
            color: Colors.grey[300],
            child: const Center(
              child: Text('Error loading image'),
            ),
          );
        },
      );
    } catch (e) {
      return Container(
        height: 200,
        color: Colors.grey[300],
        child: Center(
          child: Text('Error decoding image: $e'),
        ),
      );
    }
  }
}
```

### Step 5: Use in Your Upload Screen

Update `lib/screens/home/home_screen_upload.dart` to display the detection image:

```dart
// After detection results
if (_detectionResult != null && _detectionResult!.imageWithBoxes != null) ...[
  const SizedBox(height: 16),
  Card(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'Detection Results',
            style: Theme.of(context).textTheme.titleLarge,
          ),
        ),
        DetectionImageViewer(
          base64Image: _detectionResult!.imageWithBoxes,
        ),
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            _detectionResult!.description ?? 'No description',
            style: TextStyle(
              color: _detectionResult!.theftDetected
                  ? Colors.red
                  : Colors.green,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    ),
  ),
],
```

## 🧪 Testing the Integration

### Test 1: Health Check

Add this method to test connectivity:

```dart
Future<bool> testApiConnection() async {
  try {
    final response = await _api.get(ApiEndpoints.health);
    return response.statusCode == 200;
  } catch (e) {
    logger.error('API connection failed: $e');
    return false;
  }
}
```

Call it when the app starts:

```dart
@override
void initState() {
  super.initState();
  _checkApiConnection();
}

Future<void> _checkApiConnection() async {
  final isConnected = await DetectionService().testApiConnection();
  if (!isConnected) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Cannot connect to detection server'),
        backgroundColor: Colors.red,
      ),
    );
  }
}
```

### Test 2: Upload Test Image

```dart
// In your upload screen
Future<void> _testDetection() async {
  setState(() => _isProcessing = true);

  try {
    final result = await DetectionService().detectImageUpload(
      platformImage: _selectedImage!,
      cameraId: _selectedCamera!.id,
      cameraName: _selectedCamera!.name,
    );

    setState(() {
      _detectionResult = result;
      _isProcessing = false;
    });

    // Show result
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(result.description ?? 'Detection complete'),
        backgroundColor: result.theftDetected ? Colors.red : Colors.green,
      ),
    );
  } catch (e) {
    setState(() => _isProcessing = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Detection failed: $e'),
        backgroundColor: Colors.red,
      ),
    );
  }
}
```

## 🔍 Debugging Connection Issues

### Check API is Running

```dart
// Add this button in your debug menu
ElevatedButton(
  onPressed: () async {
    try {
      final dio = Dio();
      final response = await dio.get('${ApiEndpoints.baseUrl}/health');
      print('API Response: ${response.data}');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('API is running: ${response.data}')),
      );
    } catch (e) {
      print('API Error: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('API Error: $e')),
      );
    }
  },
  child: const Text('Test API Connection'),
),
```

### Enable Logging

Add Dio interceptor for detailed logs:

```dart
// In api_service.dart
Dio _createDio() {
  final dio = Dio(BaseOptions(
    baseURL: ApiEndpoints.baseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
  ));

  // Add logging interceptor (development only)
  if (kDebugMode) {
    dio.interceptors.add(LogInterceptor(
      request: true,
      requestHeader: true,
      requestBody: true,
      responseHeader: true,
      responseBody: true,
      error: true,
    ));
  }

  return dio;
}
```

## 📊 Expected Response Times

- **Local (localhost)**: < 1 second
- **Raspberry Pi (LAN)**: 1-3 seconds
- **Remote server**: 2-5 seconds

If detection takes longer than 10 seconds:
- Check network connectivity
- Verify Raspberry Pi isn't overloaded
- Reduce image resolution in Flutter before upload

## ✅ Integration Checklist

- [ ] Backend server is running
- [ ] Health check endpoint returns "healthy"
- [ ] Flutter app baseUrl is configured correctly
- [ ] Network permissions added to AndroidManifest.xml
- [ ] iOS allows arbitrary loads for local testing
- [ ] Test image upload works
- [ ] Detection results display correctly
- [ ] Base64 image decodes and displays
- [ ] Error handling works for network failures

## 🚀 Production Deployment

### Flutter Web

Update CORS in backend `config.py`:

```python
ALLOWED_ORIGINS = [
    "https://your-flutter-web-app.com",
]
```

### Mobile Apps

For production, use HTTPS:

```dart
static const String baseUrl = 'https://your-api-domain.com';
```

## 🎉 Success!

Your Flutter app is now connected to the YOLO backend! You should be able to:

1. Upload images from gallery
2. Take camera snapshots
3. Send images to backend
4. Receive detection results
5. Display images with bounding boxes
6. Show theft alerts

---

**Need help?** Check the [README.md](README.md) or test with Swagger UI at http://localhost:8000/docs
