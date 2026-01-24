# Alertix - Smart Supermarket Theft Detection System

A Flutter mobile application for real-time theft detection using AI-powered camera monitoring connected to a Raspberry Pi.

## Features

### Authentication
- Email/Password login and signup
- Password reset functionality
- Session persistence
- Protected routes

### Camera Monitoring
- Single Raspberry Pi camera integration
- Snapshot-based detection (NOT live video)
- Auto-refresh every 3-5 seconds
- Camera status indicator (Online/Offline)

### AI Theft Detection
- Real-time detection status from REST API
- Bounding box overlay on detected objects
- Confidence score display
- Visual warning indicators

### Alarm System
- Automatic alarm when theft detected
- Phone vibration
- Red alert banner
- Mute/unmute functionality
- Auto-stop when detection clears

### Push Notifications
- Firebase Cloud Messaging integration
- Background and foreground notifications
- Theft alert notifications with image preview

### Alert History
- List of all theft alerts
- Severity and status badges
- Pull-to-refresh
- Local caching support
- Swipe to delete

### Snapshot Gallery
- Grid and list view options
- Multi-select for bulk delete
- Full-screen preview with zoom
- Detection indicator on images

### Settings
- Dark mode support
- Notification preferences
- Alarm sound toggle
- Vibration toggle
- Server configuration

## Project Structure

```
lib/
├── auth/
│   ├── screens/
│   │   ├── login_screen.dart
│   │   ├── signup_screen.dart
│   │   └── forgot_password_screen.dart
│   ├── widgets/
│   │   ├── auth_text_field.dart
│   │   └── auth_button.dart
│   └── services/
│       └── auth_service.dart
├── core/
│   ├── constants/
│   │   └── app_constants.dart
│   ├── theme/
│   │   ├── app_theme.dart
│   │   └── app_colors.dart
│   ├── router/
│   │   └── app_router.dart
│   └── services/
│       ├── api_service.dart
│       ├── alarm_service.dart
│       ├── local_storage_service.dart
│       └── notification_service.dart
├── models/
│   ├── user_model.dart
│   ├── detection_result.dart
│   ├── alert_model.dart
│   ├── snapshot_model.dart
│   └── camera_status.dart
├── providers/
│   ├── auth_provider.dart
│   ├── theme_provider.dart
│   ├── camera_provider.dart
│   └── detection_provider.dart
├── screens/
│   ├── splash_screen.dart
│   ├── main_screen.dart
│   ├── home/
│   │   └── home_screen.dart
│   ├── alerts/
│   │   ├── alerts_screen.dart
│   │   └── alert_detail_screen.dart
│   ├── gallery/
│   │   ├── gallery_screen.dart
│   │   └── snapshot_preview_screen.dart
│   ├── profile/
│   │   └── profile_screen.dart
│   └── widgets/
│       ├── detection_overlay.dart
│       ├── alert_banner.dart
│       └── camera_status_indicator.dart
├── services/
│   ├── camera_service.dart
│   ├── detection_service.dart
│   └── alert_service.dart
└── main.dart
```

## Getting Started

### Prerequisites
- Flutter 3.x or higher
- Dart SDK
- Android Studio / Xcode
- Firebase account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/alertix_app.git
cd alertix_app
```

2. Install dependencies:
```bash
flutter pub get
```

3. Set up Firebase (see FIREBASE_SETUP.md for detailed instructions)

4. Add alarm sound file:
   - Place an alarm sound file at `assets/sounds/alarm.mp3`

5. Run the app:
```bash
flutter run
```

## API Integration

### Backend Endpoints

Configure your Raspberry Pi backend to expose these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/camera/snapshot` | GET | Get latest camera snapshot |
| `/api/camera/status` | GET | Get camera connection status |
| `/api/detection/status` | GET | Get current detection result |
| `/api/alerts` | GET | Get list of all alerts |
| `/api/alerts/{id}` | GET | Get single alert by ID |
| `/api/snapshots` | GET | Get all snapshots |

### Detection Response Format

```json
{
  "id": "detection_123",
  "theft_detected": true,
  "bounding_box": [
    {
      "x": 0.25,
      "y": 0.30,
      "width": 0.15,
      "height": 0.20,
      "confidence": 0.85,
      "label": "Suspicious Activity"
    }
  ],
  "image_url": "http://192.168.1.100/snapshot.jpg",
  "timestamp": "2024-01-23T10:30:00Z",
  "confidence": 0.85
}
```

## Configuration

### Server Address
Update the base URL in `lib/core/constants/app_constants.dart`:

```dart
static const String baseUrl = 'http://YOUR_RASPBERRY_PI_IP:5000/api';
```

### Refresh Interval
Adjust the snapshot refresh interval:

```dart
static const Duration snapshotRefreshInterval = Duration(seconds: 3);
```

## Dependencies

- **firebase_core** - Firebase initialization
- **firebase_auth** - Authentication
- **firebase_messaging** - Push notifications
- **flutter_riverpod** - State management
- **dio** - HTTP client
- **shared_preferences** - Local storage
- **hive_flutter** - Local database
- **cached_network_image** - Image caching
- **photo_view** - Image zoom
- **audioplayers** - Alarm sound
- **vibration** - Phone vibration
- **flutter_local_notifications** - Local notifications

## Screenshots

The app features a clean, professional UI with:
- Gradient accents
- Card-based layouts
- Smooth animations
- Dark mode support
- Bottom navigation
- Pull-to-refresh

## License

This project is part of a graduation project for Smart Supermarket Theft Detection System.

## Support

For issues and feature requests, please create an issue in the repository.
