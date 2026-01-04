# Entity Relationship Diagram (ERD)

## InstaGuard AI Database Schema

### Users
```
- _id: ObjectId (Primary Key)
- name: String (required)
- email: String (required, unique)
- password: String (required, hashed)
- role: String (enum: admin, operator, viewer)
- isActive: Boolean (default: true)
- lastLogin: Date
- createdAt: Date
- updatedAt: Date
```

### Cameras
```
- _id: ObjectId (Primary Key)
- name: String (required)
- location: String (required)
- ipAddress: String (required)
- port: Number (default: 8080)
- streamUrl: String (required)
- status: String (enum: online, offline, maintenance)
- isActive: Boolean (default: true)
- aiEnabled: Boolean (default: true)
- lastSeen: Date
- createdBy: ObjectId (Foreign Key -> Users)
- createdAt: Date
- updatedAt: Date
```

### Alerts
```
- _id: ObjectId (Primary Key)
- camera: ObjectId (Foreign Key -> Cameras, required)
- snapshot: ObjectId (Foreign Key -> Snapshots)
- type: String (enum: theft, suspicious, motion, other)
- severity: String (enum: low, medium, high, critical)
- status: String (enum: open, acknowledged, closed)
- description: String
- detectedAt: Date
- acknowledgedBy: ObjectId (Foreign Key -> Users)
- acknowledgedAt: Date
- closedBy: ObjectId (Foreign Key -> Users)
- closedAt: Date
- notes: Array of {
    user: ObjectId (Foreign Key -> Users)
    note: String
    createdAt: Date
  }
- metadata: {
    confidence: Number
    boundingBox: { x, y, width, height }
  }
- createdAt: Date
- updatedAt: Date
```

### Snapshots
```
- _id: ObjectId (Primary Key)
- camera: ObjectId (Foreign Key -> Cameras, required)
- alert: ObjectId (Foreign Key -> Alerts)
- imageUrl: String (required)
- thumbnailUrl: String
- filename: String (required)
- fileSize: Number
- mimeType: String (default: 'image/jpeg')
- capturedAt: Date
- tags: Array of String
- metadata: {
    width: Number
    height: Number
    aiProcessed: Boolean
    aiConfidence: Number
  }
- createdAt: Date
```

### Reports
```
- _id: ObjectId (Primary Key)
- title: String (required)
- type: String (enum: alerts, cameras, snapshots, custom)
- generatedBy: ObjectId (Foreign Key -> Users, required)
- dateRange: {
    start: Date (required)
    end: Date (required)
  }
- filters: {
    cameras: Array of ObjectId
    alertTypes: Array of String
    severities: Array of String
    statuses: Array of String
  }
- format: String (enum: pdf, csv)
- fileUrl: String
- fileSize: Number
- status: String (enum: pending, generating, completed, failed)
- metadata: {
    totalRecords: Number
    generatedAt: Date
  }
- createdAt: Date
```

### Settings
```
- _id: ObjectId (Primary Key)
- alertThresholds: {
    theft: {
      confidence: Number (0-100)
      enabled: Boolean
    }
    suspicious: {
      confidence: Number (0-100)
      enabled: Boolean
    }
    motion: {
      sensitivity: Number (0-100)
      enabled: Boolean
    }
  }
- notificationPreferences: {
    email: {
      enabled: Boolean
      criticalOnly: Boolean
    }
    push: {
      enabled: Boolean
      criticalOnly: Boolean
    }
    sms: {
      enabled: Boolean
      criticalOnly: Boolean
    }
  }
- systemSettings: {
    snapshotRetentionDays: Number
    alertRetentionDays: Number
    autoAcknowledgeAfter: Number (hours)
  }
- updatedBy: ObjectId (Foreign Key -> Users)
- updatedAt: Date
```

### AuditLog
```
- _id: ObjectId (Primary Key)
- user: ObjectId (Foreign Key -> Users, required)
- action: String (enum: user_create, user_update, user_delete, camera_create, etc.)
- resource: String (required)
- resourceId: ObjectId
- changes: Mixed
- ipAddress: String
- userAgent: String
- timestamp: Date
- createdAt: Date
```

## Relationships

1. **Users → Cameras** (One-to-Many)
   - A user can create multiple cameras
   - `Camera.createdBy` references `User._id`

2. **Cameras → Alerts** (One-to-Many)
   - A camera can have multiple alerts
   - `Alert.camera` references `Camera._id`

3. **Cameras → Snapshots** (One-to-Many)
   - A camera can have multiple snapshots
   - `Snapshot.camera` references `Camera._id`

4. **Alerts → Snapshots** (One-to-One)
   - An alert can have one associated snapshot
   - `Alert.snapshot` references `Snapshot._id`
   - `Snapshot.alert` references `Alert._id`

5. **Users → Alerts** (One-to-Many)
   - A user can acknowledge/close multiple alerts
   - `Alert.acknowledgedBy` and `Alert.closedBy` reference `User._id`

6. **Users → Reports** (One-to-Many)
   - A user can generate multiple reports
   - `Report.generatedBy` references `User._id`

7. **Users → AuditLog** (One-to-Many)
   - A user can have multiple audit log entries
   - `AuditLog.user` references `User._id`

8. **Users → Settings** (One-to-Many)
   - A user can update settings
   - `Settings.updatedBy` references `User._id`

## Indexes

- `Users.email`: Unique index
- `Alerts.camera + Alerts.status + Alerts.detectedAt`: Compound index
- `Alerts.status + Alerts.detectedAt`: Compound index
- `Snapshots.camera + Snapshots.capturedAt`: Compound index
- `Snapshots.alert`: Index
- `AuditLog.user + AuditLog.timestamp`: Compound index
- `AuditLog.action + AuditLog.timestamp`: Compound index





