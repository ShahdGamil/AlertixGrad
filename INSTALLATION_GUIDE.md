# Alertix - Installation Guide

> Complete setup guide for running the Alertix AI-powered CCTV monitoring system.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Required Software](#required-software)
3. [Installation Steps](#installation-steps)
4. [Environment Configuration](#environment-configuration)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| Storage | 10 GB free | 20 GB free |
| GPU | None (CPU works) | NVIDIA CUDA-capable GPU |
| OS | Windows 10 / Ubuntu 20.04 | Windows 11 / Ubuntu 22.04 |

---

## Required Software

### 1. Python 3.10

| | |
|---|---|
| **Version** | 3.10.x (required) |
| **Download** | https://www.python.org/downloads/release/python-31011/ |

**Windows Installation:**
1. Download the installer
2. **Important:** Check "Add Python to PATH" during installation
3. Verify installation:
   ```bash
   python --version
   ```

---

### 2. Node.js

| | |
|---|---|
| **Version** | 18.x or 20.x LTS |
| **Download** | https://nodejs.org/en/download/ |

**Verify installation:**
```bash
node --version
npm --version
```

---

### 3. MongoDB

| | |
|---|---|
| **Version** | 6.0 or 7.0 |
| **Download** | https://www.mongodb.com/try/download/community |

**Windows Installation:**
1. Download MongoDB Community Server
2. Run installer and choose "Complete" installation
3. **Important:** Select "Install MongoDB as a Service"
4. MongoDB Compass (GUI) will be installed automatically

**Verify MongoDB is running:**
```bash
mongosh
```

**Alternative - MongoDB Atlas (Cloud):**
- Create free cluster: https://www.mongodb.com/cloud/atlas/register
- Get connection string and use it in `.env`

---

### 4. Docker Desktop

| | |
|---|---|
| **Version** | Latest |
| **Download (Windows)** | https://www.docker.com/products/docker-desktop/ |
| **Download (Mac)** | https://www.docker.com/products/docker-desktop/ |
| **Download (Linux)** | https://docs.docker.com/engine/install/ |

**Windows Requirements:**
- Enable WSL 2 (Windows Subsystem for Linux)
- Enable Hyper-V

**Verify installation:**
```bash
docker --version
docker-compose --version
```

---

### 5. Git

| | |
|---|---|
| **Version** | Latest |
| **Download** | https://git-scm.com/downloads |

**Verify installation:**
```bash
git --version
```

---

### 6. Expo CLI (for Mobile App)

| | |
|---|---|
| **Version** | Latest |
| **Install via npm** | `npm install -g expo-cli` |

**For testing on mobile:**
- Download **Expo Go** app on your phone:
  - Android: https://play.google.com/store/apps/details?id=host.exp.exponent
  - iOS: https://apps.apple.com/app/expo-go/id982107779

---

### 7. Visual Studio Code (Recommended IDE)

| | |
|---|---|
| **Download** | https://code.visualstudio.com/download |

**Recommended Extensions:**
- Python
- ESLint
- Prettier
- Docker
- MongoDB for VS Code

---

## Quick Downloads Summary

| Software | Version | Download Link |
|----------|---------|---------------|
| Python | 3.10.x | https://www.python.org/downloads/release/python-31011/ |
| Node.js | 20.x LTS | https://nodejs.org/en/download/ |
| MongoDB | 7.0 | https://www.mongodb.com/try/download/community |
| Docker Desktop | Latest | https://www.docker.com/products/docker-desktop/ |
| Git | Latest | https://git-scm.com/downloads |
| VS Code | Latest | https://code.visualstudio.com/download |

---

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd "Alertix H"
```

### Step 2: Setup Backend (Node.js)

```bash
cd backend

# Install dependencies
npm install

# Copy environment file
copy .env.example .env   # Windows
# OR
cp .env.example .env     # Linux/Mac

# Edit .env file with your settings
```

### Step 3: Setup AI Service (Python)

```bash
cd ai-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate     # Windows
# OR
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env   # Windows
```

### Step 4: Setup Mobile App

```bash
cd mobile

# Install dependencies
npm install

# OR using Expo
npx expo install
```

---

## Environment Configuration

### Backend `.env` file (`backend/.env`)

```env
# Server Configuration
PORT=5000
NODE_ENV=development

# MongoDB - Change this to your MongoDB connection string
MONGODB_URI=mongodb://localhost:27017/instaguard-ai

# JWT Secret - CHANGE THIS IN PRODUCTION!
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRE=7d

# CORS
CORS_ORIGIN=http://localhost:3000

# File Upload
UPLOAD_PATH=./uploads
MAX_FILE_SIZE=10485760

# AI Service Configuration
AI_SERVICE_URL=http://localhost:5001
AI_SERVICE_API_KEY=your-secret-api-key-change-in-production
BACKEND_URL=http://localhost:5000
```

### AI Service `.env` file (`ai-service/.env`)

```env
# API Security - CHANGE THIS!
API_KEY=your-secret-api-key-change-in-production-make-it-strong

# Model Paths
MODEL_YOLOV8N_PATH=../backend/models/yolov8n/weights/best.pt
MODEL_YOLOV8S_PATH=../backend/models/yolov8s/weights/best.pt
MODEL_YOLOV8M_PATH=../backend/models/yolov8m/weights/best.pt

# Server Configuration
HOST=0.0.0.0
PORT=5001

# Device - use 'cpu' if no NVIDIA GPU
DEVICE=cpu

# Detection Thresholds
CONFIDENCE_THRESHOLD=0.25
IOU_THRESHOLD=0.45

# Logging
LOG_LEVEL=INFO

# CORS Origins
ALLOWED_ORIGINS=http://localhost:5000,http://localhost:3000
```

---

## Running the Application

### Option 1: Using the Start Script (Windows)

```bash
# From project root
start.bat
```

### Option 2: Manual Start

**Terminal 1 - Start MongoDB (if not running as service):**
```bash
mongod
```

**Terminal 2 - Start AI Service (Docker):**
```bash
cd ai-service
docker-compose up
```

**Terminal 3 - Start Backend:**
```bash
cd backend
npm run dev
```

**Terminal 4 - Start Mobile App:**
```bash
cd mobile
npx expo start
```

### Verify Services are Running

| Service | URL | Expected Response |
|---------|-----|-------------------|
| Backend Health | http://localhost:5000/api/health | `{ "status": "ok" }` |
| AI Service Health | http://localhost:5001/health | `{ "status": "healthy" }` |

---

## Port Configuration

| Service | Port |
|---------|------|
| Backend API | 5000 |
| AI Service | 5001 |
| MongoDB | 27017 |
| Expo Dev Server | 19000, 19001, 19002 |

---

## Troubleshooting

### MongoDB Connection Error

```
Error: connect ECONNREFUSED 127.0.0.1:27017
```

**Solution:**
1. Make sure MongoDB is installed
2. Start MongoDB service:
   - Windows: `net start MongoDB`
   - Linux: `sudo systemctl start mongod`

### Docker Issues

```
Error: Cannot connect to Docker daemon
```

**Solution:**
1. Make sure Docker Desktop is running
2. On Windows, ensure WSL 2 is enabled
3. Restart Docker Desktop

### Python Module Not Found

```
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
1. Make sure virtual environment is activated
2. Reinstall requirements:
   ```bash
   pip install -r requirements.txt
   ```

### Port Already in Use

```
Error: EADDRINUSE: address already in use :::5000
```

**Solution:**
- Windows:
  ```bash
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  ```
- Linux/Mac:
  ```bash
  lsof -i :5000
  kill -9 <PID>
  ```

### CUDA/GPU Issues

If you don't have an NVIDIA GPU:
1. Open `ai-service/.env`
2. Change `DEVICE=cuda` to `DEVICE=cpu`

---

## AI Model Weights

The YOLOv8 model weights should be placed in:
```
backend/models/
├── yolov8n/
│   └── weights/
│       └── best.pt
├── yolov8s/
│   └── weights/
│       └── best.pt
└── yolov8m/
    └── weights/
        └── best.pt
```

---

## Technology Stack Summary

| Layer | Technology | Version |
|-------|------------|---------|
| **AI Service** | Python | 3.10 |
| | FastAPI | 0.109.0 |
| | PyTorch | 2.1.2 |
| | YOLOv8 (ultralytics) | 8.1.11 |
| | OpenCV | 4.9.0.80 |
| **Backend** | Node.js | 18.x / 20.x |
| | Express | 4.18.2 |
| | Mongoose | 8.0.3 |
| **Database** | MongoDB | 6.0 / 7.0 |
| **Mobile** | React Native | 0.72.10 |
| | Expo | 49.0.15 |
| **DevOps** | Docker | Latest |

---

## Need Help?

- Check the project README for more details
- Review the `.env.example` files for configuration options
- Make sure all services are running before testing

---

*Last updated: January 2025*
