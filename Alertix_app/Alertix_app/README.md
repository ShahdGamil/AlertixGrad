# Alertix - Smart Supermarket Theft Detection System

A Flutter mobile application for real-time theft detection using AI-powered camera monitoring with FastAPI backend.

## What's New (v3.0.0)

### 🔐 User Authentication System
- JWT-based authentication (no Firebase required)
- Secure password hashing with bcrypt
- SQLite user database
- Token-based session management

### 📧 Email Notification System
- Gmail SMTP integration
- Automatic email alerts on theft detection
- HTML-formatted emails with image attachments
- Configurable retry logic

### 📷 Camera Persistence
- Cameras saved to SQLite database
- Persistent across app restarts
- Full CRUD operations (Create, Read, Update, Delete)

### 🗄️ Alert History Storage
- All alerts stored in SQLite database
- Mark alerts as read/unread
- Delete individual or all alerts
- Persistent alert history

## Features

### User Authentication (JWT-Based)
- ✅ Email/Password registration and login
- ✅ JWT token-based authentication
- ✅ Secure password hashing with bcrypt
- ✅ Session persistence with local storage
- ✅ Protected API routes
- ✅ Auto-login on app restart

### Email Notifications (NEW)
- ✅ Gmail SMTP integration
- ✅ Automatic email alerts when theft is detected
- ✅ HTML-formatted emails with alert details
- ✅ Image attachment support
- ✅ Retry logic for failed sends
- ✅ Configurable recipient email

### Camera Monitoring
- ✅ Multiple RTSP camera support
- ✅ Camera persistence across app restarts
- ✅ Add/Edit/Delete cameras
- ✅ Snapshot-based detection
- ✅ Auto-refresh every 3-5 seconds
- ✅ Camera status indicator (Online/Offline)

### AI Theft Detection (YOLO)
- ✅ Real-time theft detection using YOLO ensemble model
- ✅ FastAPI backend with high performance
- ✅ 6 detection classes (Theft, Normal, Product, etc.)
- ✅ Bounding box overlay on detected objects
- ✅ Confidence score display
- ✅ Visual warning indicators

### Alarm System
- ✅ Automatic alarm when theft detected
- ✅ Phone vibration
- ✅ Red alert banner
- ✅ Mute/unmute functionality
- ✅ Auto-stop when detection clears

### Alert History
- ✅ List of all theft alerts
- ✅ Persistent storage in SQLite database
- ✅ Severity and status badges
- ✅ Pull-to-refresh
- ✅ Mark alerts as read/unread
- ✅ Swipe to delete

### Snapshot Gallery
- ✅ Grid and list view options
- ✅ Multi-select for bulk delete
- ✅ Full-screen preview with zoom
- ✅ Detection indicator on images

### Settings
- ✅ Dark mode support
- ✅ Notification preferences
- ✅ Alarm sound toggle
- ✅ Vibration toggle
- ✅ Server configuration

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

**Backend:**
- Python 3.8+
- YOLO model file: `best (4).pt`
- Gmail account with App Password

**Flutter App:**
- Flutter 3.x or higher
- Dart SDK
- Android Studio / Xcode

### Installation

#### 1. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

Configure `backend/config.py` with your email credentials.

Start the server:
```bash
python backend.py
```

See [backend/README.md](backend/README.md) for detailed instructions.

#### 2. Flutter App Setup

```bash
cd ..  # Go back to root directory
flutter pub get
```

Update `lib/core/constants/app_constants.dart` with your backend URL.

Add alarm sound file at `assets/sounds/alarm.mp3` (optional).

Run the app:
```bash
flutter run
```

## API Integration

The app connects to a FastAPI backend server running on port 8003. See [backend/README.md](backend/README.md) for detailed backend setup.

### Backend Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| **Authentication** |
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login and get JWT token |
| `/auth/me` | GET | Get current user (protected) |
| `/auth/logout` | POST | Logout user |
| **Detection** |
| `/predict` | POST | Upload image for theft detection |
| `/health` | GET | Backend health check |
| **Cameras** |
| `/cameras` | GET | Get all cameras |
| `/cameras` | POST | Add new camera |
| `/cameras/{id}` | GET | Get camera by ID |
| `/cameras/{id}` | PUT | Update camera |
| `/cameras/{id}` | DELETE | Delete camera |
| `/cameras/clear/all` | DELETE | Clear all cameras |
| **Alerts** |
| `/alerts` | GET | Get all alerts |
| `/alerts/{id}` | GET | Get alert by ID |
| `/alerts/{id}/read` | PUT | Mark alert as read |
| `/alerts/{id}` | DELETE | Delete alert |
| `/alerts/clear` | DELETE | Clear all alerts |

### Detection Response Format

```json
{
  "theft_detected": true,
  "detections": [
    {
      "bbox": [100.5, 200.3, 300.7, 400.2],
      "confidence": 0.87,
      "class": 5,
      "class_name": "theft"
    }
  ],
  "total_detections": 1,
  "overall_confidence": 0.87,
  "description": "Theft detected! 1 suspicious object(s) found.",
  "camera_id": "camera_001",
  "camera_name": "Front Door Camera",
  "timestamp": "2026-01-26T10:35:00",
  "image_with_boxes": "base64_encoded_image..."
}
```

## Configuration

### Backend Server Setup

1. Navigate to the backend directory and follow setup instructions in [backend/README.md](backend/README.md)

2. Configure email notifications in `backend/config.py`:
```python
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_APP_PASSWORD = "your_16_char_app_password"  # Generate from Google Account
RECEIVER_EMAIL = "security@yourstore.com"
```

3. Start the backend server:
```bash
cd backend
python backend.py
```

### Flutter App Configuration

Update the base URL in `lib/core/constants/app_constants.dart`:

```dart
// For localhost testing
static const String baseUrl = 'http://localhost:8003';

// For Android emulator
// static const String baseUrl = 'http://10.0.2.2:8003';

// For real device (use your computer's IP)
// static const String baseUrl = 'http://192.168.1.100:8003';
```

### Refresh Interval

Adjust the snapshot refresh interval:

```dart
static const Duration snapshotRefreshInterval = Duration(seconds: 3);
```

## Dependencies

### Flutter App
- **flutter_riverpod** - State management
- **dio** - HTTP client for API calls
- **shared_preferences** - Token and user data storage
- **hive_flutter** - Local database for caching
- **cached_network_image** - Image caching
- **photo_view** - Image zoom and preview
- **audioplayers** - Alarm sound playback
- **vibration** - Phone vibration on alerts
- **flutter_local_notifications** - Local notifications

### Backend (Python)
- **fastapi** - High-performance web framework
- **uvicorn** - ASGI server
- **ultralytics** - YOLO model implementation
- **opencv-python** - Image processing
- **PyJWT** - JWT token generation
- **bcrypt** - Password hashing
- **python-multipart** - File upload support

See [backend/requirements.txt](backend/requirements.txt) for full backend dependencies.

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
