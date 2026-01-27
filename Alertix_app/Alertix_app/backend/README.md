# Alertix YOLO Theft Detection API Backend

Complete Python REST API backend for the Alertix Flutter app using FastAPI and YOLO ensemble model.

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Desktop/Server Installation](#desktopserver-installation)
  - [Raspberry Pi Installation](#raspberry-pi-installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Email Notifications](#email-notifications)
- [Testing the API](#testing-the-api)
- [Flutter Integration](#flutter-integration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Core Detection
- ✅ FastAPI web framework (high performance, async support)
- ✅ YOLO ensemble model loading at startup
- ✅ Real-time theft detection (Class 5 = Theft, Class 4 = Normal)
- ✅ REST API endpoints for image upload and prediction
- ✅ Bounding box visualization with class labels
- ✅ Base64 encoded image response for Flutter
- ✅ CORS enabled for Flutter web and mobile apps
- ✅ Optimized for Raspberry Pi deployment
- ✅ Health check endpoint
- ✅ Comprehensive error handling and logging
- ✅ Flutter-ready JSON response format

### User Authentication (NEW)
- ✅ User registration with email/password
- ✅ Secure password hashing with bcrypt
- ✅ JWT token-based authentication
- ✅ Protected API routes
- ✅ SQLite database for user storage

### Email Notifications (NEW)
- ✅ Gmail SMTP integration
- ✅ Automatic email alerts on theft detection
- ✅ HTML email with alert details
- ✅ Image attachment support
- ✅ Retry logic for failed sends

### Persistent Storage (NEW)
- ✅ SQLite database for alerts
- ✅ SQLite database for cameras
- ✅ Camera state persistence across app restarts

---

## 📦 Prerequisites

### Required Files

1. **YOLO Model File**: `Final_Copy_of_YOLO_Ensemble_Colab_Full_(3)_final.pt`
   - Place this file in the `backend/` directory

### System Requirements

**Minimum (Raspberry Pi 4):**
- 2GB RAM
- Python 3.8+
- 8GB SD card

**Recommended:**
- 4GB+ RAM
- Python 3.9+
- GPU (optional, for faster inference)

---

## 🚀 Installation

### Desktop/Server Installation

#### 1. Clone the Repository

```bash
cd backend/
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install PyTorch (CPU version)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
pip install -r requirements.txt
```

**For GPU Support (NVIDIA CUDA):**

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

#### 4. Verify Installation

```bash
python -c "import fastapi; import ultralytics; import cv2; print('✓ All dependencies installed!')"
```

---

### Raspberry Pi Installation

#### 1. Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### 2. Install System Dependencies

```bash
# Install Python and pip
sudo apt-get install python3-pip python3-dev -y

# Install OpenCV dependencies
sudo apt-get install libopencv-dev python3-opencv -y

# Install NumPy dependencies
sudo apt-get install libatlas-base-dev gfortran -y

# Install image libraries
sudo apt-get install libjpeg-dev libtiff-dev libpng-dev -y
```

#### 3. Install Python Packages

```bash
# Upgrade pip
pip3 install --upgrade pip

# Install PyTorch CPU version (optimized for ARM)
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
pip3 install -r requirements.txt
```

#### 4. Verify Installation

```bash
python3 -c "import fastapi; import ultralytics; import cv2; print('✓ All dependencies installed!')"
```

---

## ⚙️ Configuration

Edit `config.py` to customize settings without modifying the main backend code:

```python
# Model path
MODEL_PATH = "best (4).pt"

# Confidence threshold
CONFIDENCE_THRESHOLD = 0.25

# Server settings
HOST = "0.0.0.0"
PORT = 8003

# Class names
CLASS_NAMES = {
    0: "Customer-Bagpack",
    1: "Product",
    2: "Product-Picked",
    3: "Shopping-Cart",
    4: "normal",
    5: "theft"
}

# Email Configuration (Gmail SMTP)
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_APP_PASSWORD = "your_app_password_here"  # Generate from Google Account
RECEIVER_EMAIL = "your_email@gmail.com"
EMAIL_NOTIFICATIONS_ENABLED = True

# JWT Authentication
JWT_SECRET_KEY = "your-secret-key-change-in-production"
JWT_ACCESS_TOKEN_EXPIRE_HOURS = 24
JWT_ALGORITHM = "HS256"
PASSWORD_MIN_LENGTH = 6
```

### Gmail App Password Setup

To use Gmail SMTP, you need to generate an App Password:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification (required)
3. Go to "App passwords" under 2-Step Verification
4. Generate a new app password for "Mail"
5. Copy the 16-character password to `EMAIL_APP_PASSWORD` in config.py

---

## 🏃 Running the Server

### Method 1: Using Python Directly

```bash
# Development mode (auto-reload enabled)
python backend.py

# Or with Python 3
python3 backend.py
```

### Method 2: Using Uvicorn Directly

```bash
# Development mode
uvicorn backend:app --host 0.0.0.0 --port 8000 --reload

# Production mode (Raspberry Pi)
uvicorn backend:app --host 0.0.0.0 --port 8000 --workers 1
```

### Server Output

When the server starts successfully, you should see:

```
======================================================================
Starting Alertix YOLO Theft Detection API Server
======================================================================
INFO:     Loading YOLO model from Final_Copy_of_YOLO_Ensemble_Colab_Full_(3)_final.pt...
INFO:     ✓ Model loaded successfully and warmed up!
INFO:     Server ready to accept requests!
======================================================================
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Accessing the API

- **API Root**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📡 API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API server is running.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-01-25T10:30:00.123456",
  "model_loaded": true,
  "api_version": "1.0.0",
  "message": "Alertix YOLO Theft Detection API is running"
}
```

### 2. Predict Theft

**POST** `/predict`

Upload an image for theft detection.

**Request (multipart/form-data):**

- `image` (required): Image file (JPEG, PNG, etc.)
- `camera_id` (optional): Camera ID from Flutter app
- `camera_name` (optional): Camera name from Flutter app
- `confidence_threshold` (optional): Minimum confidence (default: 0.25)
- `include_image` (optional): Include base64 image (default: true)

**Response:**

```json
{
  "theft_detected": true,
  "detections": [
    {
      "bbox": [100.5, 200.3, 300.7, 400.2],
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
  "image_with_boxes": "base64_encoded_image_here..."
}
```

### 3. Root Endpoint

**GET** `/`

API information and available endpoints.

---

## 🔐 Authentication

The backend includes a complete user authentication system using JWT tokens.

### Authentication Endpoints

#### Register New User

**POST** `/auth/register`

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "user_id": "uuid-string",
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-01-26T12:00:00",
    "is_active": true
  }
}
```

#### Login

**POST** `/auth/login`

```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "user_id": "uuid-string",
    "full_name": "John Doe",
    "email": "john@example.com",
    "is_active": true
  }
}
```

#### Get Current User

**GET** `/auth/me`

Requires `Authorization: Bearer <token>` header.

**Response (200):**
```json
{
  "user_id": "uuid-string",
  "full_name": "John Doe",
  "email": "john@example.com",
  "is_active": true
}
```

#### Logout

**POST** `/auth/logout`

Logs out the current user (client should discard the token).

### Using Authentication in Flutter

```dart
// Login
final response = await api.post('/auth/login', data: {
  'email': email,
  'password': password,
});
final token = response.data['access_token'];

// Store token
await LocalStorageService.saveAuthToken(token);

// Use token in requests (automatic via ApiService interceptor)
// The ApiService adds Authorization header automatically
```

---

## 📧 Email Notifications

The backend automatically sends email alerts when theft is detected.

### How It Works

1. When `/predict` detects theft (`theft_detected: true`)
2. An alert is saved to the database
3. An email is sent to the configured receiver email
4. Email includes: alert details, camera info, confidence score, and image attachment

### Email Content

- **Subject**: `🚨 THEFT ALERT - [Camera Name] - Alertix`
- **Body**: HTML formatted with:
  - Alert timestamp
  - Camera name and ID
  - Detection confidence score
  - Action recommendations
- **Attachment**: Detection image (if available)

### Configuration

In `config.py`:

```python
# Enable/disable email notifications
EMAIL_NOTIFICATIONS_ENABLED = True

# Gmail SMTP settings
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_APP_PASSWORD = "your_16_char_app_password"

# Recipient email
RECEIVER_EMAIL = "security@yourstore.com"

# Retry settings
EMAIL_RETRY_ATTEMPTS = 1
```

### Testing Email

```bash
# Test email sending (requires valid SMTP config)
curl -X POST "http://localhost:8003/predict" \
  -F "image=@theft_test_image.jpg" \
  -F "camera_id=test_cam" \
  -F "camera_name=Test Camera"
```

If theft is detected and email is configured, you'll receive an email notification.

---

## 📷 Camera Persistence

Cameras are stored in SQLite database and persist across app restarts.

### Camera Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cameras` | Get all cameras |
| GET | `/cameras/{id}` | Get camera by ID |
| POST | `/cameras` | Add new camera |
| PUT | `/cameras/{id}` | Update camera |
| DELETE | `/cameras/{id}` | Delete camera |
| DELETE | `/cameras/clear/all` | Delete all cameras |

### Camera Model

```json
{
  "id": "camera_uuid",
  "name": "Front Door Camera",
  "rtsp_url": "rtsp://192.168.1.100:554/stream",
  "username": "admin",
  "password": "encrypted_password",
  "is_active": true,
  "created_at": "2026-01-26T12:00:00",
  "updated_at": "2026-01-26T12:00:00"
}
```

---

## 🚨 Alerts Storage

Alerts are stored in SQLite database for history and analysis.

### Alert Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/alerts` | Get all alerts |
| GET | `/alerts/{id}` | Get alert by ID |
| PUT | `/alerts/{id}/read` | Mark alert as read |
| DELETE | `/alerts/{id}` | Delete alert |
| DELETE | `/alerts/clear` | Clear all alerts |

---

## 🧪 Testing the API

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

### Test 2: Upload Image (using curl)

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "image=@test_image.jpg" \
  -F "camera_id=camera_001" \
  -F "camera_name=Test Camera" \
  -F "confidence_threshold=0.25" \
  -F "include_image=true"
```

### Test 3: Python Test Script

Create `test_api.py`:

```python
import requests

# API endpoint
url = "http://localhost:8000/predict"

# Open image file
with open("test_image.jpg", "rb") as f:
    files = {"image": f}
    data = {
        "camera_id": "camera_001",
        "camera_name": "Test Camera",
        "confidence_threshold": 0.25,
        "include_image": True
    }

    # Send POST request
    response = requests.post(url, files=files, data=data)

    # Print response
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
```

Run the test:

```bash
python test_api.py
```

### Test 4: Using Swagger UI

1. Open browser: http://localhost:8000/docs
2. Click on **POST /predict**
3. Click **"Try it out"**
4. Upload an image file
5. Fill in optional fields
6. Click **"Execute"**
7. View the response

---

## 📱 Flutter Integration

### Update Flutter API Service

Update your Flutter `lib/core/constants/app_constants.dart`:

```dart
class ApiEndpoints {
  // For Raspberry Pi on local network
  static const String baseUrl = 'http://192.168.1.100:8000';

  // For localhost testing (Android emulator)
  // static const String baseUrl = 'http://10.0.2.2:8000';

  // For localhost testing (iOS simulator)
  // static const String baseUrl = 'http://localhost:8000';

  // For production server
  // static const String baseUrl = 'https://your-domain.com';

  static const String detectUpload = '/predict';
  static const String health = '/health';
}
```

### Update Detection Service

Your existing `detection_service.dart` should work perfectly:

```dart
Future<DetectionResult> detectImageUpload({
  required PlatformImage platformImage,
  required String cameraId,
  String? cameraName,
}) async {
  try {
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
  } catch (e) {
    // Handle error
  }
}
```

### Parse Response in Flutter

```dart
class DetectionResult {
  final bool theftDetected;
  final List<Detection> detections;
  final String? imageWithBoxes; // base64 string
  final double? overallConfidence;
  final String? description;

  factory DetectionResult.fromJson(Map<String, dynamic> json) {
    return DetectionResult(
      theftDetected: json['theft_detected'] ?? false,
      detections: (json['detections'] as List?)
          ?.map((d) => Detection.fromJson(d))
          .toList() ?? [],
      imageWithBoxes: json['image_with_boxes'],
      overallConfidence: json['overall_confidence']?.toDouble(),
      description: json['description'],
    );
  }
}

class Detection {
  final List<double> bbox;
  final double confidence;
  final int classId;
  final String className;

  factory Detection.fromJson(Map<String, dynamic> json) {
    return Detection(
      bbox: (json['bbox'] as List).map((e) => e.toDouble()).toList(),
      confidence: json['confidence'].toDouble(),
      classId: json['class'],
      className: json['class_name'],
    );
  }
}
```

---

## 🚀 Deployment

### Raspberry Pi Deployment

#### 1. Transfer Files

```bash
# Using SCP
scp -r backend/ pi@raspberrypi.local:/home/pi/alertix/

# Or use FileZilla, WinSCP, etc.
```

#### 2. Install Dependencies

SSH into Raspberry Pi and follow the [Raspberry Pi Installation](#raspberry-pi-installation) steps.

#### 3. Run Server on Boot (systemd)

Create service file:

```bash
sudo nano /etc/systemd/system/alertix-api.service
```

Add content:

```ini
[Unit]
Description=Alertix YOLO Theft Detection API
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/alertix/backend
ExecStart=/usr/bin/python3 /home/pi/alertix/backend/backend.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable alertix-api.service
sudo systemctl start alertix-api.service

# Check status
sudo systemctl status alertix-api.service

# View logs
sudo journalctl -u alertix-api.service -f
```

#### 4. Configure Firewall (Optional)

```bash
# Allow port 8000
sudo ufw allow 8000/tcp
sudo ufw enable
```

### Production Server Deployment

For deploying to a cloud server (AWS, DigitalOcean, etc.), use:

```bash
# Install Gunicorn for production
pip install gunicorn

# Run with Gunicorn
gunicorn backend:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Use **Nginx** as a reverse proxy for HTTPS support.

---

## 🐛 Troubleshooting

### Issue 1: Model file not found

**Error**: `Model file not found: Final_Copy_of_YOLO_Ensemble_Colab_Full_(3)_final.pt`

**Solution**:
- Ensure the model file is in the `backend/` directory
- Check the filename matches exactly
- Update `MODEL_PATH` in `config.py` if needed

### Issue 2: Port already in use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use a different port
```

### Issue 3: Out of memory on Raspberry Pi

**Solution**:
- Reduce `MAX_IMAGE_WIDTH` and `MAX_IMAGE_HEIGHT` in `config.py`
- Use lighter OpenCV version: `opencv-python-headless`
- Increase swap space:
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Issue 4: Slow inference on Raspberry Pi

**Solution**:
- Ensure using CPU version of PyTorch
- Reduce image resolution
- Lower `CONFIDENCE_THRESHOLD`
- Consider using YOLO Nano or YOLO-S models

### Issue 5: CORS errors from Flutter

**Solution**:
- Verify `ALLOWED_ORIGINS` in `config.py`
- Check Flutter app is using correct API URL
- Ensure server allows cross-origin requests

---

## 📄 File Structure

```
backend/
├── backend.py              # Main FastAPI application
├── config.py               # Configuration settings (server, email, JWT)
├── database.py             # SQLite database (users, alerts, cameras)
├── auth_service.py         # JWT authentication & password hashing
├── email_service.py        # Gmail SMTP email notifications
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── alertix.db              # SQLite database file (auto-created)
└── best (4).pt             # YOLO model file
```

### New Files Added

| File | Purpose |
|------|---------|
| `auth_service.py` | Handles JWT token generation, password hashing with bcrypt, user authentication |
| `email_service.py` | Gmail SMTP integration, sends HTML emails with image attachments on theft detection |
| `database.py` | SQLite database management for users, alerts, and cameras |

---

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review API logs for detailed error messages
3. Test with Swagger UI at http://localhost:8000/docs
4. Verify model file exists and is accessible

---

## 🎉 Success Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed successfully
- [ ] Model file in correct location
- [ ] Server starts without errors
- [ ] Health check endpoint returns "healthy"
- [ ] Test image upload works
- [ ] Flutter app can connect to API
- [ ] Detections appear correctly in Flutter app

---

**Happy Coding! 🚀**
