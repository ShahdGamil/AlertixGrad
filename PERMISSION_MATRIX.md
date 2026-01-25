# Permission Matrix - InstaGuard AI

## Role-Based Access Control (RBAC)

This document outlines the permissions for each user role across all features and API endpoints.

## Roles

1. **Admin**: Full system access
2. **Operator**: Camera control and alert management
3. **Viewer**: Read-only access

## Feature Permissions

| Feature | Admin | Operator | Viewer |
|---------|-------|----------|--------|
| **Dashboard** | ✅ View | ✅ View | ✅ View |
| **Cameras** | | | |
| - View List | ✅ | ✅ | ✅ |
| - View Details | ✅ | ✅ | ✅ |
| - Live View | ✅ | ✅ | ✅ |
| - Create | ✅ | ✅ | ❌ |
| - Edit | ✅ | ✅ (Limited) | ❌ |
| - Delete | ✅ | ❌ | ❌ |
| - Control (Zoom/Pan) | ✅ | ✅ | ❌ |
| **Alerts** | | | |
| - View List | ✅ | ✅ | ✅ |
| - View Details | ✅ | ✅ | ✅ |
| - Acknowledge | ✅ | ✅ | ❌ |
| - Close | ✅ | ✅ | ❌ |
| - Add Notes | ✅ | ✅ | ❌ |
| - Delete | ✅ | ❌ | ❌ |
| **Snapshots** | | | |
| - View Gallery | ✅ | ✅ | ✅ |
| - Download | ✅ | ✅ | ✅ |
| - Create | ✅ | ❌ | ❌ |
| - Delete | ✅ | ❌ | ❌ |
| **Reports** | | | |
| - View List | ✅ | ✅ | ✅ |
| - Generate | ✅ | ✅ | ❌ |
| - Export (PDF/CSV) | ✅ | ✅ | ✅ |
| - Download | ✅ | ✅ | ✅ |
| **Settings** | | | |
| - View | ✅ | ✅ | ✅ |
| - Update | ✅ | ❌ | ❌ |
| **User Management** | | | |
| - View Users | ✅ | ❌ | ❌ |
| - Create User | ✅ | ❌ | ❌ |
| - Edit User | ✅ | ❌ | ❌ |
| - Delete User | ✅ | ❌ | ❌ |
| **Billing** | | | |
| - View | ✅ | ❌ | ❌ |
| **Notifications** | ✅ | ✅ | ✅ |
| **Audit Logs** | ✅ | ❌ | ❌ |

## API Endpoint Permissions

### Authentication
| Endpoint | Admin | Operator | Viewer | Public |
|----------|-------|----------|--------|--------|
| POST /auth/register | ✅ | ✅ | ✅ | ✅ |
| POST /auth/login | ✅ | ✅ | ✅ | ✅ |
| GET /auth/me | ✅ | ✅ | ✅ | ❌ |
| PUT /auth/profile | ✅ | ✅ | ✅ | ❌ |
| PUT /auth/change-password | ✅ | ✅ | ✅ | ❌ |

### Users
| Endpoint | Admin | Operator | Viewer | Public |
|----------|-------|----------|--------|--------|
| GET /users | ✅ | ❌ | ❌ | ❌ |
| POST /users | ✅ | ❌ | ❌ | ❌ |
| GET /users/:id | ✅ | ❌ | ❌ | ❌ |
| PUT /users/:id | ✅ | ❌ | ❌ | ❌ |
| DELETE /users/:id | ✅ | ❌ | ❌ | ❌ |

### Cameras
| Endpoint | Admin | Operator | Viewer | Public |
|----------|-------|----------|--------|--------|
| GET /cameras | ✅ | ✅ | ✅ | ❌ |
| GET /cameras/:id | ✅ | ✅ | ✅ | ❌ |
| POST /cameras | ✅ | ✅ | ❌ | ❌ |
| PUT /cameras/:id | ✅ | ✅ (Limited) | ❌ | ❌ |
| DELETE /cameras/:id | ✅ | ❌ | ❌ | ❌ |
| PATCH /cameras/:id/status | ✅ | ✅ | ❌ | ❌ |

### Alerts
| Endpoint | Admin | Operator | Viewer | Public |
|----------|-------|----------|--------|--------|
| GET /alerts | ✅ | ✅ | ✅ | ❌ |
| GET /alerts/:id | ✅ | ✅ | ✅ | ❌ |
| POST /alerts | ✅ | ❌ | ❌ | ❌ |
| POST /alerts/:id/acknowledge | ✅ | ✅ | ❌ | ❌ |
| POST /alerts/:id/close | ✅ | ✅ | ❌ | ❌ |
| POST /alerts/:id/notes | ✅ | ✅ | ❌ | ❌ |
| DELETE /alerts/:id | ✅ | ❌ | ❌ | ❌ |

### Snapshots
| Endpoint | Admin | Operator | Viewer | Public |
|----------|-------|----------|--------|--------|
| GET /snapshots | ✅ | ✅ | ✅ | ❌ |
| GET /snapshots/:id | ✅ | ✅ | ✅ | ❌ |
| GET /snapshots/:id/download | ✅ | ✅ | ✅ | ❌ |
| POST /snapshots | ✅ | ❌ | ❌ | ❌ |
| DELETE /snapshots/:id | ✅ | ❌ | ❌ | ❌ |

### Reports
| Endpoint | Admin | Operator | Viewer | Public |
|----------|-------|----------|--------|--------|
| GET /reports | ✅ | ✅ | ✅ | ❌ |
| GET /reports/:id | ✅ | ✅ | ✅ | ❌ |
| POST /reports | ✅ | ✅ | ❌ | ❌ |
| GET /reports/:id/download | ✅ | ✅ | ✅ | ❌ |

### Settings
| Endpoint | Admin | Operator | Viewer | Public |
|----------|-------|----------|--------|--------|
| GET /settings | ✅ | ✅ | ✅ | ❌ |
| PUT /settings | ✅ | ❌ | ❌ | ❌ |

### Billing
| Endpoint | Admin | Operator | Viewer | Public |
|----------|-------|----------|--------|--------|
| GET /billing | ✅ | ❌ | ❌ | ❌ |
| GET /billing/invoices | ✅ | ❌ | ❌ | ❌ |

### Notifications
| Endpoint | Admin | Operator | Viewer | Public |
|----------|-------|----------|--------|--------|
| GET /notifications | ✅ | ✅ | ✅ | ❌ |
| GET /notifications/unread-count | ✅ | ✅ | ✅ | ❌ |
| POST /notifications/:id/read | ✅ | ✅ | ✅ | ❌ |

## Business Rules

### Operator Limitations
- Can only edit limited camera fields (name, location, status)
- Cannot delete cameras, alerts, or snapshots
- Cannot manage users or billing
- Cannot update system settings

### Viewer Limitations
- Read-only access to all data
- Cannot create, update, or delete any resources
- Cannot generate reports (but can view existing ones)
- Cannot acknowledge or close alerts

### Admin Privileges
- Full CRUD access to all resources
- Can manage all users
- Can update system settings
- Can access audit logs
- Can manage billing

## Security Notes

1. All endpoints (except login/register) require JWT authentication
2. Role checks are performed server-side using middleware
3. Self-modification restrictions:
   - Users cannot change their own role
   - Users cannot deactivate their own account
   - Users cannot delete their own account
4. Audit logging is enabled for all destructive operations
5. Password hashing is enforced using bcrypt





