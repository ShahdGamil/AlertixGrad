# InstaGuard AI - API Documentation

Base URL: `http://localhost:5000/api/v1`

All endpoints require authentication except `/auth/login` and `/auth/register`.

## Authentication

### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": { ... },
    "token": "jwt_token_here"
  }
}
```

### POST /auth/login
Login with email and password.

**Request Body:**
```json
{
  "email": "admin@instaguard.ai",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": { ... },
    "token": "jwt_token_here"
  }
}
```

### GET /auth/me
Get current user profile. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": { ... }
  }
}
```

## Users

### GET /users
Get all users. **Admin only.**

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `role` (optional): Filter by role
- `search` (optional): Search by name or email

### POST /users
Create a new user. **Admin only.**

**Request Body:**
```json
{
  "name": "New User",
  "email": "newuser@example.com",
  "password": "password123",
  "role": "viewer"
}
```

### GET /users/:id
Get user by ID. **Admin only.**

### PUT /users/:id
Update user. **Admin only.**

### DELETE /users/:id
Delete user. **Admin only.**

## Cameras

### GET /cameras
Get all cameras. **All authenticated users.**

**Query Parameters:**
- `page` (optional): Page number
- `limit` (optional): Items per page
- `status` (optional): Filter by status (online/offline/maintenance)
- `search` (optional): Search by name or location

### GET /cameras/:id
Get camera by ID. **All authenticated users.**

### POST /cameras
Create a new camera. **Admin, Operator.**

**Request Body:**
```json
{
  "name": "Front Door",
  "location": "Main Entrance",
  "ipAddress": "192.168.1.100",
  "port": 8080,
  "streamUrl": "rtsp://192.168.1.100:8080/stream",
  "status": "online",
  "aiEnabled": true
}
```

### PUT /cameras/:id
Update camera. **Admin, Operator.**

### DELETE /cameras/:id
Delete camera. **Admin only.**

### PATCH /cameras/:id/status
Update camera status. **Admin, Operator.**

## Alerts

### GET /alerts
Get all alerts. **All authenticated users.**

**Query Parameters:**
- `page` (optional): Page number
- `limit` (optional): Items per page
- `status` (optional): Filter by status (open/acknowledged/closed)
- `severity` (optional): Filter by severity
- `type` (optional): Filter by type
- `camera` (optional): Filter by camera ID
- `startDate` (optional): Start date filter
- `endDate` (optional): End date filter

### GET /alerts/:id
Get alert by ID. **All authenticated users.**

### POST /alerts/:id/acknowledge
Acknowledge an alert. **Admin, Operator.**

### POST /alerts/:id/close
Close an alert. **Admin, Operator.**

### POST /alerts/:id/notes
Add a note to an alert. **Admin, Operator.**

**Request Body:**
```json
{
  "note": "Investigating the incident"
}
```

### DELETE /alerts/:id
Delete alert. **Admin only.**

## Snapshots

### GET /snapshots
Get all snapshots. **All authenticated users.**

**Query Parameters:**
- `page` (optional): Page number
- `limit` (optional): Items per page
- `camera` (optional): Filter by camera ID
- `alert` (optional): Filter by alert ID
- `startDate` (optional): Start date filter
- `endDate` (optional): End date filter
- `tags` (optional): Filter by tags

### GET /snapshots/:id
Get snapshot by ID. **All authenticated users.**

### GET /snapshots/:id/download
Download snapshot image. **All authenticated users.**

### POST /snapshots
Create snapshot. **Admin only.**

### DELETE /snapshots/:id
Delete snapshot. **Admin only.**

## Reports

### GET /reports
Get all reports. **Admin, Operator, Viewer.**

**Query Parameters:**
- `page` (optional): Page number
- `limit` (optional): Items per page

### GET /reports/:id
Get report by ID. **Admin, Operator, Viewer.**

### POST /reports
Generate a new report. **Admin, Operator.**

**Request Body:**
```json
{
  "type": "alerts",
  "dateRange": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "filters": {
    "cameras": ["camera_id_1"],
    "alertTypes": ["theft", "suspicious"],
    "severities": ["high", "critical"]
  },
  "format": "pdf"
}
```

### GET /reports/:id/download
Download report file. **Admin, Operator, Viewer.**

## Settings

### GET /settings
Get system settings. **All authenticated users.**

### PUT /settings
Update system settings. **Admin only.**

**Request Body:**
```json
{
  "alertThresholds": {
    "theft": {
      "confidence": 75,
      "enabled": true
    }
  },
  "notificationPreferences": {
    "email": {
      "enabled": true,
      "criticalOnly": false
    }
  }
}
```

## Billing

### GET /billing
Get billing information. **Admin only.**

### GET /billing/invoices
Get invoices. **Admin only.**

## Notifications

### GET /notifications
Get notifications. **All authenticated users.**

**Query Parameters:**
- `page` (optional): Page number
- `limit` (optional): Items per page
- `unreadOnly` (optional): Filter unread only

### GET /notifications/unread-count
Get unread notification count. **All authenticated users.**

### POST /notifications/:id/read
Mark notification as read. **All authenticated users.**

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "success": false,
  "message": "Error message here"
}
```

**Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Authentication

Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```





