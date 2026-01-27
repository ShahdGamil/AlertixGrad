# Alertix App - Complete Requirements & Setup Guide

**Version:** 1.0.0+1
**Last Updated:** January 2026
**Project:** Smart Supermarket Theft Detection System
**Description:** AI-powered security monitoring with real-time alerts

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Dependencies](#dependencies)
3. [Installation & Setup](#installation--setup)
4. [Project Structure](#project-structure)
5. [Features Implemented](#features-implemented)
6. [Configuration](#configuration)
7. [Running the App](#running-the-app)
8. [Known Issues](#known-issues)
9. [Future Development](#future-development)
10. [For Future Developers](#for-future-developers)

---

## 🖥️ System Requirements

### Development Environment
- **Flutter SDK:** >=3.0.0 <4.0.0
- **Dart SDK:** Included with Flutter
- **IDE:** VS Code or Android Studio (recommended)
- **Git:** Latest version

### Target Platforms
- ✅ **Web (Chrome/Edge)** - Primary development platform
- ✅ **Android** - API Level 33+ (Android 13+)
- ⏳ **iOS** - Configured but not fully tested

### Backend Requirements (Optional)
- Backend API for production deployment
- AI model endpoint for theft detection
- Image storage service

---

## 📦 Dependencies

### Production Dependencies

#### **Core Flutter**
```yaml
flutter:
  sdk: flutter
```

#### **State Management**
```yaml
flutter_riverpod: ^2.4.9          # Reactive state management
riverpod_annotation: ^2.3.3       # Code generation annotations
```

#### **Networking**
```yaml
dio: ^5.4.0                       # HTTP client for API calls
```

#### **Local Storage**
```yaml
shared_preferences: ^2.2.2        # Simple key-value storage
hive: ^2.2.3                      # NoSQL database
hive_flutter: ^1.1.0              # Flutter integration for Hive
path_provider: ^2.1.2             # File system paths
```

#### **UI Components**
```yaml
cached_network_image: ^3.3.1      # Cached image loading
flutter_svg: ^2.0.9               # SVG image support
shimmer: ^3.0.0                   # Loading skeleton animations
photo_view: ^0.14.0               # Image zoom/pan viewer
flutter_staggered_grid_view: ^0.7.0  # Grid layout for gallery
```

#### **Utilities**
```yaml
intl: ^0.18.1                     # Internationalization & date formatting
uuid: ^4.3.3                      # Unique ID generation
permission_handler: ^11.2.0       # Runtime permissions
```

#### **Audio & Vibration**
```yaml
audioplayers: ^5.2.1              # Audio playback for alarms
vibration: ^1.8.4                 # Haptic feedback
```

#### **Notifications**
```yaml
flutter_local_notifications: ^16.3.2  # Local notifications
```

#### **Image Handling**
```yaml
image: ^4.1.7                     # Image manipulation
image_picker: ^1.0.7              # Camera/gallery access
```

#### **Icons**
```yaml
cupertino_icons: ^1.0.6           # iOS-style icons
flutter_vector_icons: ^2.0.0      # Additional icon packs
```

### Development Dependencies

```yaml
flutter_test:
  sdk: flutter
flutter_lints: ^3.0.1             # Linting rules
build_runner: ^2.4.8              # Code generation tool
riverpod_generator: ^2.3.9        # Riverpod code generation
hive_generator: ^2.0.1            # Hive adapter generation
```

### Disabled Dependencies (Temporarily for Web Testing)

The following Firebase dependencies are commented out but will be needed for mobile deployment:

```yaml
# firebase_core: ^2.24.2
# firebase_auth: ^4.16.0
# firebase_messaging: ^14.7.10
# cloud_firestore: ^4.14.0
```

**Why disabled?** Firebase doesn't fully support web testing in the current development phase. These will be re-enabled for mobile deployment.

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Alertix_app
```

### Step 2: Install Flutter Dependencies

```bash
flutter pub get
```

### Step 3: Generate Required Code

The app uses code generation for Hive models and Riverpod providers:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

**Note:** Run this command whenever you:
- First clone the project
- Modify models with `@HiveType` annotations
- See errors about missing `.g.dart` files

### Step 4: Add Missing Assets

**CRITICAL:** The app references an alarm sound that doesn't exist yet:

```
assets/sounds/alarm.mp3
```

**You must add this file** or the app will crash when an alarm is triggered.

Recommended sources:
- Create your own alarm sound
- Download from free sound libraries (freesound.org, zapsplat.com)
- Use a simple beep/alert tone

**File specifications:**
- Format: MP3
- Duration: 3-5 seconds (will loop)
- Size: <500KB recommended

### Step 5: Verify Setup

Check that everything is installed correctly:

```bash
flutter doctor -v
```

Expected output should show:
- ✓ Flutter SDK installed
- ✓ Connected device (web/Android emulator)
- ✓ No critical issues

---

## 📁 Project Structure

```
Alertix_app/
├── android/                    # Android-specific configuration
├── ios/                        # iOS-specific configuration
├── web/                        # Web-specific configuration
├── lib/
│   ├── main.dart              # App entry point
│   │
│   ├── auth/                  # Authentication module
│   │   ├── screens/           # Login, signup, forgot password
│   │   ├── services/          # Auth service (mock)
│   │   └── widgets/           # Reusable auth components
│   │
│   ├── core/                  # Core infrastructure
│   │   ├── constants/         # App-wide constants
│   │   ├── router/            # Navigation logic
│   │   ├── services/          # Core services (alarm, notification, API, storage)
│   │   └── theme/             # Color scheme and themes
│   │
│   ├── models/                # Data models
│   │   ├── models.dart        # Barrel export
│   │   ├── user_model.dart
│   │   ├── camera_model.dart
│   │   ├── camera_model.g.dart  # Generated - DO NOT EDIT
│   │   ├── camera_status.dart
│   │   ├── alert_model.dart
│   │   ├── snapshot_model.dart
│   │   └── detection_result.dart
│   │
│   ├── providers/             # Riverpod state management
│   │   ├── auth_provider.dart
│   │   ├── camera_provider.dart
│   │   ├── cameras_provider.dart
│   │   ├── detection_provider.dart
│   │   └── theme_provider.dart
│   │
│   ├── services/              # Business logic services
│   │   ├── camera_service.dart
│   │   ├── detection_service.dart
│   │   └── alert_service.dart
│   │
│   └── screens/               # UI screens
│       ├── splash_screen.dart
│       ├── main_screen.dart   # Tab navigation
│       │
│       ├── home/
│       │   └── home_screen_upload.dart  # Image upload detection
│       │
│       ├── cameras/
│       │   ├── cameras_screen.dart
│       │   └── widgets/
│       │       └── add_camera_dialog.dart
│       │
│       ├── gallery/
│       │   ├── gallery_screen.dart
│       │   └── snapshot_preview_screen.dart
│       │
│       ├── alerts/
│       │   ├── alerts_screen.dart
│       │   └── alert_detail_screen.dart
│       │
│       ├── profile/
│       │   └── profile_screen.dart
│       │
│       └── widgets/           # Shared widgets
│           ├── alert_banner.dart
│           ├── camera_status_indicator.dart
│           └── detection_overlay.dart
│
├── assets/
│   ├── images/                # App images (logo, etc.)
│   ├── sounds/
│   │   └── alarm.mp3          # REQUIRED - Add this file!
│   └── icons/                 # Custom icons
│
├── pubspec.yaml               # Dependencies
├── analysis_options.yaml      # Linter configuration
├── REQUIREMENTS.md            # This file
├── FIREBASE_SETUP.md          # Firebase configuration guide
└── README.md                  # Basic project info
```

---

## ✨ Features Implemented

### 1. **Authentication System** ✅
- Login screen
- Sign up with email/password
- Forgot password flow
- Mock authentication (no backend required)
- Session persistence with SharedPreferences

**Status:** Fully functional with mock backend

### 2. **Camera Management** ✅
- Add new cameras with name/location/ID
- View list of all cameras
- Active/inactive status indicators
- Edit camera details
- Delete cameras with confirmation
- Persistent storage with Hive

**Status:** Fully functional

### 3. **Image Upload Detection** ✅
- Select camera from dropdown
- Upload image from camera or gallery
- Send to AI detection API
- Display detection results with:
  - Bounding boxes on detected objects
  - Confidence scores
  - Animated overlays
  - Success/failure status
- Auto-create alerts for positive detections
- Mock detection (30% random detection rate)

**Status:** UI complete, uses mock AI (backend integration pending)

### 4. **Alert Management** ✅
- View list of all theft alerts
- Alert details with:
  - Timestamp
  - Camera location
  - Detection image
  - Confidence score
- Delete alerts with confirmation
- Filter by status (pending/reviewed/resolved)
- Badge indicator on navigation

**Status:** Fully functional

### 5. **Snapshot Gallery** ✅
- Grid view of camera snapshots
- Full-screen image viewer
- Zoom and pan functionality
- Timestamp display
- Pull-to-refresh

**Status:** Fully functional

### 6. **Alarm System** ✅
- Audio alarm when theft detected
- Vibration feedback
- Mute/unmute controls
- Loop playback
- Volume control

**Status:** ⚠️ Requires `alarm.mp3` file to work

### 7. **Local Notifications** ✅
- Theft detection notifications
- Tap to open alert details
- Custom notification sound
- Badge on app icon

**Status:** Functional on mobile, limited on web

### 8. **Dark/Light Theme** ✅
- Toggle in profile settings
- Persistent theme preference
- Smooth transition animations
- Custom color schemes

**Status:** Fully functional

### 9. **Profile & Settings** ✅
- User information display
- App statistics
- Theme toggle
- Account management
- Logout functionality

**Status:** Fully functional

---

## ⚙️ Configuration

### API Endpoints

Edit `lib/core/constants/app_constants.dart` to configure backend:

```dart
class ApiEndpoints {
  static const String baseUrl = 'https://your-api-url.com/api/v1';

  // Authentication
  static const String login = '/auth/login';
  static const String signup = '/auth/signup';
  static const String logout = '/auth/logout';

  // Cameras
  static const String cameras = '/cameras';
  static const String cameraStatus = '/cameras/{id}/status';

  // Detection
  static const String detectUpload = '/detection/upload';
  static const String detectionStatus = '/detection/status';
  static const String detectionHistory = '/detection/history';

  // Alerts
  static const String alerts = '/alerts';
}
```

### App Constants

Also in `app_constants.dart`:

```dart
class AppConstants {
  // App Info
  static const String appName = 'Alertix';
  static const String appVersion = '1.0.0';

  // Timing
  static const Duration snapshotRefreshInterval = Duration(seconds: 5);
  static const Duration cameraStatusTimeout = Duration(seconds: 10);

  // Storage Keys
  static const String authTokenKey = 'auth_token';
  static const String userDataKey = 'user_data';
  static const String themeKey = 'theme_mode';

  // Hive Boxes
  static const String camerasBox = 'cameras';
  static const String alertsBox = 'alerts';
}
```

---

## 🏃 Running the App

### Web (Development)

**Chrome:**
```bash
flutter run -d chrome
```

**Edge (Recommended for Windows):**
```bash
flutter run -d edge
```

**Web with hot reload:**
```bash
flutter run -d web-server --web-port 8080
```

### Android Emulator

**Start emulator:**
```bash
# List available emulators
flutter emulators

# Launch emulator
flutter emulators --launch <emulator-id>
```

**Run app:**
```bash
flutter run -d <device-id>
```

### Physical Device

**Enable USB debugging on Android device**

**Run:**
```bash
flutter devices  # List connected devices
flutter run -d <device-id>
```

### Build for Production

**Android APK:**
```bash
flutter build apk --release
```

**Android App Bundle (for Google Play):**
```bash
flutter build appbundle --release
```

**Web:**
```bash
flutter build web --release
```

**iOS (requires Mac):**
```bash
flutter build ios --release
```

---

## ⚠️ Known Issues

### 1. Missing Alarm Sound File
**Issue:** App references `assets/sounds/alarm.mp3` which doesn't exist
**Impact:** Crash when alarm triggers
**Fix:** Add MP3 file to assets/sounds/
**Priority:** HIGH

### 2. Firebase Disabled
**Issue:** Firebase dependencies commented out
**Impact:** No cloud auth, no push notifications
**Fix:** Uncomment Firebase dependencies when deploying to mobile
**Priority:** MEDIUM (for mobile deployment)

### 3. Mock Detection Service
**Issue:** Detection uses random mock data instead of real AI
**Impact:** Detection results are fake
**Fix:** Implement real backend integration in `detection_service.dart`
**Priority:** HIGH (for production)

### 4. No Real Camera Feed
**Issue:** App only supports image upload, no live streaming
**Impact:** Cannot monitor cameras in real-time
**Fix:** Implement WebRTC or HLS streaming
**Priority:** LOW (future feature)

### 5. Image.file() Not Supported on Web
**Issue:** Fixed - Now uses conditional rendering
**Impact:** None (already fixed)
**Fix:** Uses `kIsWeb` check to render Image.network() for web, Image.file() for mobile
**Priority:** RESOLVED ✅

---

## 🔮 Future Development

### Planned Features

#### **High Priority**
1. **Real Backend Integration**
   - Replace mock services with actual API calls
   - Implement proper authentication
   - Connect to AI model endpoint

2. **Real AI Detection**
   - Integrate with YOLO/TensorFlow model
   - Support multiple detection classes
   - Improve confidence thresholds

3. **Firebase Re-enablement**
   - Uncomment Firebase dependencies
   - Set up Firebase project
   - Enable push notifications
   - Cloud Firestore for data sync

#### **Medium Priority**
4. **Live Camera Streaming**
   - Implement WebRTC or HLS player
   - Real-time detection on stream
   - Multi-camera grid view

5. **Advanced Alert Management**
   - Alert categorization
   - Search and filter
   - Export to PDF/CSV
   - Email notifications

6. **Analytics Dashboard**
   - Detection statistics
   - Time-based graphs
   - Heatmaps of detection areas
   - Camera performance metrics

#### **Low Priority**
7. **Multi-language Support**
   - Use existing `intl` package
   - Add language selection
   - Translate all strings

8. **Cloud Backup**
   - Auto-sync to cloud storage
   - Backup/restore settings
   - Multi-device support

---

## 👥 For Future Developers

### Getting Started

1. **Read this entire document** - It contains everything you need
2. **Check Project Structure section** - Understand the architecture
3. **Review `app_constants.dart`** - All configuration is here
4. **Run `flutter pub get` and code generation** - See Installation section
5. **Add the alarm sound file** - CRITICAL first step

### Architecture Overview

This app uses **Flutter Riverpod** for state management with a **feature-based architecture**:

```
Feature (e.g., Cameras)
├── Screen (UI)
├── Provider (State)
├── Service (Business Logic)
└── Model (Data)
```

**Example flow:**
1. User taps "Add Camera" button in `cameras_screen.dart`
2. Dialog shown from `add_camera_dialog.dart` widget
3. On submit, calls `cameras_provider.dart` provider
4. Provider calls `camera_service.dart` service
5. Service makes API call (currently returns mock data)
6. Service saves to Hive using `local_storage_service.dart`
7. Provider updates state
8. Screen rebuilds with new camera in list

### Code Generation

**When to run code generation:**
- After modifying `@HiveType` annotated classes
- After modifying `@riverpod` annotated providers
- When you see "missing .g.dart" errors

**Command:**
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### Important Files to Know

| File | Purpose |
|------|---------|
| `main.dart` | App initialization, MaterialApp setup |
| `app_router.dart` | All navigation routes |
| `app_constants.dart` | All configuration |
| `models.dart` | Import all models from here |
| `detection_service.dart` | AI detection logic - NEEDS BACKEND |
| `api_service.dart` | HTTP client wrapper |

### Testing the App

**Test with mock data (no backend needed):**
1. Login with any email/password
2. Add cameras from Cameras tab
3. Upload image from Home tab
4. Check Alerts tab for auto-generated alerts

**Test accounts (mock):**
- Email: `test@test.com`
- Password: `anything`

All authentication is mocked - any credentials will work.

### Common Tasks

#### Add a New Screen
1. Create screen file in `lib/screens/<feature>/`
2. Add route in `app_router.dart`
3. Navigate using: `Navigator.pushNamed(context, '/route-name')`

#### Add a New Model
1. Create model in `lib/models/`
2. Add `@HiveType` if it needs local storage
3. Add to `models.dart` barrel export
4. Run code generation
5. Register adapter in `local_storage_service.dart`

#### Add a New Provider
1. Create provider in `lib/providers/`
2. Use `StateNotifierProvider` for mutable state
3. Use `Provider` for immutable/computed values
4. Use `FutureProvider` for async data
5. Run code generation if using `@riverpod`

#### Connect to Real Backend
1. Update `baseUrl` in `app_constants.dart`
2. Modify service methods to use real API
3. Remove mock data generators
4. Handle error responses properly
5. Add loading states

### Debugging Tips

**App crashes on startup:**
- Run `flutter clean && flutter pub get`
- Run code generation
- Check if all dependencies installed

**Can't upload images on web:**
- Already fixed with `kIsWeb` check
- Make sure image_picker is up to date

**Alarm doesn't play:**
- Add `assets/sounds/alarm.mp3` file
- Check file permissions
- Test on mobile, not web (web has audio restrictions)

**State not updating:**
- Make sure you're using `ConsumerWidget` or `ConsumerStatefulWidget`
- Use `ref.watch()` to listen to providers
- Use `ref.read()` for one-time reads
- Check if provider is properly invalidated

**Build errors:**
- Run `flutter clean`
- Run `flutter pub get`
- Run code generation
- Restart IDE
- Check for typos in import paths

### Contribution Guidelines

When making changes:

1. **Follow existing architecture** - Don't introduce new patterns
2. **Use Riverpod for state** - No setState() in business logic
3. **Use services for API calls** - Keep screens clean
4. **Generate code after model changes** - Don't forget build_runner
5. **Test on web AND mobile** - Both platforms supported
6. **Document complex logic** - Add comments
7. **Use meaningful names** - Be descriptive
8. **Keep widgets small** - Extract reusable components

### Resources

- **Flutter Documentation:** https://docs.flutter.dev/
- **Riverpod Documentation:** https://riverpod.dev/
- **Hive Documentation:** https://docs.hivedb.dev/
- **Dio Documentation:** https://pub.dev/packages/dio

---

## 🎯 Quick Start Checklist

- [ ] Clone repository
- [ ] Run `flutter pub get`
- [ ] Run code generation
- [ ] Add `alarm.mp3` to assets/sounds/
- [ ] Run `flutter run -d edge` (or chrome/emulator)
- [ ] Test basic functionality
- [ ] Review `app_constants.dart`
- [ ] Read architecture overview
- [ ] Set up backend (when ready)
- [ ] Enable Firebase (when ready for mobile)

---

**Document Version:** 1.0
**Last Updated:** January 24, 2026
**Maintained By:** Alertix Development Team
