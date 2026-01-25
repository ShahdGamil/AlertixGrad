# AlertixGrad – AI-Powered Retail Theft Detection System

AlertixGrad is an end-to-end AI-powered CCTV monitoring system designed for retail theft detection.  
The project combines **deep learning (YOLOv8)** with a **full-stack application** to provide real-time alerts, camera monitoring, reports, and role-based access control.

---

## System Overview

AlertixGrad consists of three main components:

### 1️⃣ AI & Computer Vision Module
- Retail theft detection using **YOLOv8**
- Trained on CCTV surveillance data
- Detects normal behavior vs theft incidents
- Exports models for production deployment

### 2️⃣ Backend Server
- Node.js + Express
- MongoDB database
- JWT-based authentication
- Role-based access (Admin / Operator / Viewer)
- Report generation (PDF & CSV)

### 3️⃣ Mobile Application
- React Native (Expo)
- Real-time alerts
- Camera monitoring
- Snapshot gallery
- Reports and dashboards

---

## Tech Stack

### AI / ML
- Python
- YOLOv8 (Ultralytics)
- PyTorch
- OpenCV
- Albumentations

### Backend
- Node.js
- Express.js
- MongoDB + Mongoose
- JWT Authentication
- bcrypt
- PDFKit & CSV-Writer

### Mobile App
- React Native (Expo)
- React Navigation
- React Native Paper
- Axios
- AsyncStorage

---

## Detected Classes (YOLOv8)

| ID | Class | Description |
|----|-------|-------------|
| 0 | Customer-Backpack | Customer carrying a backpack |
| 1 | Product | Product on shelf |
| 2 | Product-Picked | Product picked up |
| 3 | Shopping-Cart | Shopping cart |
| 4 | Normal | Normal shopping behavior |
| 5 | **Theft** | **Shoplifting / theft behavior** |

---

## Model Performance (YOLOv8s)

- **mAP@0.5 (Validation)**: 84.27%
- **mAP@0.5 (Test)**: 77.86%
- **Precision**: ~78%
- **Recall**: ~75%

The model shows strong generalization and stable convergence across training and test datasets.

---

## Project Structure

