# ⚡ Quick Start Guide

Get your YOLO API running in 5 minutes!

## 🚀 Fast Setup

### Step 1: Place Your Model File

```bash
# Put your model file in the backend/ directory
backend/
├── Final_Copy_of_YOLO_Ensemble_Colab_Full_(3)_final.pt  ← Your model here
├── backend.py
└── requirements.txt
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install everything
pip install -r requirements.txt
```

### Step 3: Run the Server

```bash
python backend.py
```

You should see:

```
======================================================================
Starting Alertix YOLO Theft Detection API Server
======================================================================
✓ Model loaded successfully and warmed up!
Server ready to accept requests!
======================================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test It

Open your browser:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or run the test script:

```bash
python test_api.py
```

## 📱 Connect Flutter App

Update your Flutter `lib/core/constants/app_constants.dart`:

```dart
class ApiEndpoints {
  // Local development
  static const String baseUrl = 'http://localhost:8000';

  // Android emulator
  // static const String baseUrl = 'http://10.0.2.2:8000';

  // Raspberry Pi (replace with your Pi's IP)
  // static const String baseUrl = 'http://192.168.1.100:8000';

  static const String detectUpload = '/predict';
  static const String health = '/health';
}
```

## ✅ Verify Everything Works

1. ✓ Server starts without errors
2. ✓ http://localhost:8000/health returns "healthy"
3. ✓ http://localhost:8000/docs shows Swagger UI
4. ✓ Test script passes all tests
5. ✓ Flutter app can upload images

## 🐛 Common Issues

### "Model file not found"
- Check the filename matches exactly
- Ensure the .pt file is in the backend/ directory

### "Port 8000 already in use"
- Change port in config.py or kill the process using port 8000

### "Out of memory" (Raspberry Pi)
- Reduce image size in config.py
- Use opencv-python-headless

## 🎉 Success!

Your API is running! Now:

1. Test with Swagger UI: http://localhost:8000/docs
2. Upload an image
3. Check the response JSON
4. Connect your Flutter app

## 📚 Next Steps

- Read [README.md](README.md) for detailed documentation
- Deploy to Raspberry Pi (see README)
- Set up systemd service for auto-start
- Configure CORS for production

---

**Need help?** Check the [README.md](README.md) or [Troubleshooting section](README.md#troubleshooting)
