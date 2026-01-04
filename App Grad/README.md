# InstaGuard AI - CCTV Monitoring System

A comprehensive CCTV monitoring system for supermarket theft detection with AI-powered alerts, camera management, and admin dashboard.

## Project Overview

InstaGuard AI is a full-stack application consisting of:
- **Backend**: Node.js + Express + MongoDB
- **Frontend**: React Native (Expo)
- **Features**: Real-time camera monitoring, AI-powered theft detection, alert management, snapshot gallery, reports, and user management

## Tech Stack

### Backend
- Node.js with Express
- MongoDB with Mongoose
- JWT Authentication
- bcrypt for password hashing
- PDFKit & CSV-Writer for report generation

### Frontend
- React Native (Expo)
- React Navigation
- React Native Paper (UI Components)
- Axios for API calls
- AsyncStorage for local storage

## Installation

### Prerequisites
- Node.js (v16 or higher)
- MongoDB (v5 or higher)
- npm or yarn
- Expo CLI (for mobile app)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Update `.env` with your configuration:
```
PORT=5000
NODE_ENV=development
MONGODB_URI=mongodb://localhost:27017/instaguard-ai
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRE=7d
CORS_ORIGIN=http://localhost:3000
```

5. Seed the database:
```bash
npm run seed
```

6. Start the server:
```bash
npm run dev
```

The backend will run on `http://localhost:5000`

### Mobile App Setup

1. Navigate to mobile directory:
```bash
cd mobile
```

2. Install dependencies:
```bash
npm install
```

3. Update API configuration in `src/config/api.js`:
```javascript
const API_BASE_URL = 'http://YOUR_IP_ADDRESS:5000/api/v1';
// For Android emulator, use: http://10.0.2.2:5000/api/v1
// For iOS simulator, use: http://localhost:5000/api/v1
```

4. Start the Expo development server:
```bash
npm start
```

5. Scan the QR code with Expo Go app or press `a` for Android / `i` for iOS

## Default Login Credentials

After seeding the database, you can use these credentials:

- **Admin**: `admin@instaguard.ai` / `admin123`
- **Operator**: `operator@instaguard.ai` / `operator123`
- **Viewer**: `viewer@instaguard.ai` / `viewer123`

## Project Structure

```
.
├── backend/
│   ├── controllers/      # Route controllers
│   ├── models/           # Mongoose models
│   ├── routes/           # Express routes
│   ├── middleware/       # Auth & audit middleware
│   ├── utils/            # Utility functions
│   ├── scripts/          # Seed scripts
│   └── server.js         # Entry point
│
├── mobile/
│   ├── src/
│   │   ├── screens/      # Screen components
│   │   ├── navigation/   # Navigation setup
│   │   ├── context/      # Context providers
│   │   ├── config/       # Configuration
│   │   └── theme/        # Theme configuration
│   └── App.js            # Entry point
│
└── README.md
```

## Features

### User Roles

1. **Admin**
   - Full CRUD on users, cameras, alerts, settings
   - View/export reports
   - Access audit logs
   - Billing management

2. **Operator**
   - View & control cameras (zoom/pan/fullscreen)
   - Acknowledge/close alerts
   - Add notes to alerts
   - Generate/export reports
   - Edit camera info (limited)

3. **Viewer**
   - Read-only access
   - View dashboard
   - Camera view-only
   - Gallery/reports read-only

### Core Features

- **Authentication**: Login/Signup with JWT
- **Dashboard**: Active cameras, recent alerts, system status
- **Cameras**: List, detail view, live stream with controls
- **Alerts**: Timeline, detail view, acknowledge/close, add notes
- **Snapshots**: Gallery with filters and download
- **Reports**: Generate and export CSV & PDF
- **Settings**: Alert thresholds, notification preferences
- **User Management**: Admin-only user CRUD
- **Notifications**: Real-time alert notifications
- **Billing**: Subscription and usage information

## API Documentation

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for detailed API endpoints.

## Database Schema

See [ERD.md](./ERD.md) for Entity Relationship Diagram.

## Permission Matrix

See [PERMISSION_MATRIX.md](./PERMISSION_MATRIX.md) for role-based permissions.

## Testing

Run tests:
```bash
cd backend
npm test
```

## Development

### Backend Development
```bash
cd backend
npm run dev  # Uses nodemon for auto-reload
```

### Mobile Development
```bash
cd mobile
npm start  # Expo development server
```

## Production Deployment

### Backend
1. Set `NODE_ENV=production` in `.env`
2. Use a process manager like PM2
3. Configure MongoDB connection string
4. Set secure JWT secret

### Mobile
1. Build with Expo:
```bash
expo build:android
expo build:ios
```

## Security Considerations

- Passwords are hashed using bcrypt
- JWT tokens expire after 7 days
- Role-based access control on all endpoints
- Audit logging for destructive operations
- Input validation on all endpoints

## License

This project is for educational purposes (Graduation Project).

## Support

For issues or questions, please refer to the project documentation or contact the development team.





