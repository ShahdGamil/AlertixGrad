"""
SQLite Database Manager for Alertix Backend
============================================
Handles persistent storage of theft alerts and camera states.

Tables:
- alerts: Stores all theft detection alerts
- cameras: Stores camera metadata and last known states
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)

# Database file path (in backend directory)
DB_PATH = os.path.join(os.path.dirname(__file__), "alertix.db")


class DatabaseManager:
    """Manages SQLite database operations for alerts and cameras."""

    def __init__(self, db_path: str = DB_PATH):
        """Initialize database manager and create tables if needed."""
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def init_database(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    camera_id TEXT NOT NULL,
                    camera_name TEXT,
                    timestamp TEXT NOT NULL,
                    theft_detected INTEGER NOT NULL,
                    confidence_score REAL,
                    detected_class TEXT,
                    description TEXT,
                    bbox_data TEXT,
                    image_base64 TEXT,
                    status TEXT DEFAULT 'new'
                )
            """)

            # Create cameras table (full camera configuration)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cameras (
                    camera_id TEXT PRIMARY KEY,
                    camera_name TEXT NOT NULL,
                    location TEXT,
                    camera_number TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    user_id TEXT DEFAULT 'default_user',
                    last_active_time TEXT,
                    last_detection_status TEXT,
                    last_image_snapshot TEXT
                )
            """)

            # Create users table for authentication
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)

            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp
                ON alerts(timestamp DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_camera
                ON alerts(camera_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_status
                ON alerts(status)
            """)

            logger.info(f"✓ Database initialized at: {self.db_path}")

    # ============================================================================
    # ALERTS OPERATIONS
    # ============================================================================

    def save_alert(
        self,
        camera_id: str,
        camera_name: Optional[str],
        timestamp: str,
        theft_detected: bool,
        confidence_score: Optional[float],
        detected_class: Optional[str],
        description: Optional[str],
        bbox_data: Optional[List[Dict]],
        image_base64: Optional[str] = None,
    ) -> int:
        """
        Save a new alert to the database.

        Returns:
            alert_id: The ID of the newly created alert
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Convert bbox_data to JSON string
            bbox_json = json.dumps(bbox_data) if bbox_data else None

            cursor.execute("""
                INSERT INTO alerts (
                    camera_id, camera_name, timestamp, theft_detected,
                    confidence_score, detected_class, description,
                    bbox_data, image_base64, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                camera_id,
                camera_name,
                timestamp,
                1 if theft_detected else 0,
                confidence_score,
                detected_class,
                description,
                bbox_json,
                image_base64,
                'new'
            ))

            alert_id = cursor.lastrowid
            logger.info(f"✓ Alert saved: ID={alert_id}, camera={camera_id}")
            return alert_id

    def get_all_alerts(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all alerts ordered by newest first.

        Args:
            limit: Maximum number of alerts to return (None = all)

        Returns:
            List of alert dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM alerts ORDER BY timestamp DESC"
            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            rows = cursor.fetchall()

            alerts = []
            for row in rows:
                alert = dict(row)
                # Parse bbox_data JSON
                if alert['bbox_data']:
                    alert['bbox_data'] = json.loads(alert['bbox_data'])
                # Convert theft_detected to boolean
                alert['theft_detected'] = bool(alert['theft_detected'])
                alerts.append(alert)

            return alerts

    def get_alert_by_id(self, alert_id: int) -> Optional[Dict[str, Any]]:
        """Get a single alert by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts WHERE alert_id = ?", (alert_id,))
            row = cursor.fetchone()

            if row:
                alert = dict(row)
                if alert['bbox_data']:
                    alert['bbox_data'] = json.loads(alert['bbox_data'])
                alert['theft_detected'] = bool(alert['theft_detected'])
                return alert
            return None

    def mark_alert_as_viewed(self, alert_id: int) -> bool:
        """Mark an alert as viewed."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE alerts SET status = 'viewed' WHERE alert_id = ?
            """, (alert_id,))

            updated = cursor.rowcount > 0
            if updated:
                logger.info(f"✓ Alert {alert_id} marked as viewed")
            return updated

    def clear_all_alerts(self) -> int:
        """Delete all alerts from database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alerts")
            deleted_count = cursor.rowcount
            logger.info(f"✓ Cleared {deleted_count} alerts")
            return deleted_count

    def get_alert_count(self) -> int:
        """Get total number of alerts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM alerts")
            return cursor.fetchone()[0]

    # ============================================================================
    # CAMERAS OPERATIONS
    # ============================================================================

    def save_camera(
        self,
        camera_id: str,
        camera_name: str,
        location: Optional[str] = None,
        camera_number: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[str] = None,
        user_id: str = 'default_user',
    ) -> str:
        """
        Save or update a camera configuration.

        Returns:
            camera_id: The ID of the saved camera
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if created_at is None:
                created_at = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO cameras (
                    camera_id, camera_name, location, camera_number,
                    is_active, created_at, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(camera_id) DO UPDATE SET
                    camera_name = excluded.camera_name,
                    location = excluded.location,
                    camera_number = excluded.camera_number,
                    is_active = excluded.is_active,
                    user_id = excluded.user_id
            """, (
                camera_id,
                camera_name,
                location,
                camera_number,
                1 if is_active else 0,
                created_at,
                user_id
            ))

            logger.info(f"✓ Camera saved: {camera_id} ({camera_name})")
            return camera_id

    def update_camera_state(
        self,
        camera_id: str,
        camera_name: Optional[str],
        last_detection_status: str,
        last_image_snapshot: Optional[str] = None,
    ):
        """Update camera's last detection state."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()

            cursor.execute("""
                UPDATE cameras SET
                    last_active_time = ?,
                    last_detection_status = ?,
                    last_image_snapshot = ?
                WHERE camera_id = ?
            """, (
                timestamp,
                last_detection_status,
                last_image_snapshot,
                camera_id
            ))

            if cursor.rowcount == 0:
                # Camera doesn't exist, create it
                cursor.execute("""
                    INSERT INTO cameras (
                        camera_id, camera_name, created_at, user_id,
                        last_active_time, last_detection_status, last_image_snapshot
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    camera_id,
                    camera_name or f"Camera {camera_id[:8]}",
                    timestamp,
                    'default_user',
                    timestamp,
                    last_detection_status,
                    last_image_snapshot
                ))

            logger.debug(f"✓ Camera state updated: {camera_id}")

    def get_all_cameras(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all cameras, optionally filtered by user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if user_id:
                cursor.execute("""
                    SELECT * FROM cameras WHERE user_id = ?
                    ORDER BY created_at DESC
                """, (user_id,))
            else:
                cursor.execute("SELECT * FROM cameras ORDER BY created_at DESC")

            cameras = []
            for row in cursor.fetchall():
                camera = dict(row)
                camera['is_active'] = bool(camera.get('is_active', 1))
                cameras.append(camera)

            logger.info(f"✓ Retrieved {len(cameras)} cameras")
            return cameras

    def get_camera_by_id(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Get camera by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cameras WHERE camera_id = ?", (camera_id,))
            row = cursor.fetchone()
            if row:
                camera = dict(row)
                camera['is_active'] = bool(camera.get('is_active', 1))
                return camera
            return None

    def delete_camera(self, camera_id: str) -> bool:
        """Delete a camera by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cameras WHERE camera_id = ?", (camera_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"✓ Camera deleted: {camera_id}")
            return deleted

    def clear_all_cameras(self, user_id: Optional[str] = None) -> int:
        """Delete all cameras, optionally for a specific user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("DELETE FROM cameras WHERE user_id = ?", (user_id,))
            else:
                cursor.execute("DELETE FROM cameras")
            deleted_count = cursor.rowcount
            logger.info(f"✓ Cleared {deleted_count} cameras")
            return deleted_count

    # ============================================================================
    # USER AUTHENTICATION OPERATIONS
    # ============================================================================

    def create_user(
        self,
        user_id: str,
        full_name: str,
        email: str,
        password_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new user account.

        Returns:
            User dict if created, None if email already exists
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            created_at = datetime.now().isoformat()

            try:
                cursor.execute("""
                    INSERT INTO users (user_id, full_name, email, password_hash, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, full_name, email.lower(), password_hash, created_at))

                logger.info(f"✓ User created: {email}")
                return {
                    "user_id": user_id,
                    "full_name": full_name,
                    "email": email.lower(),
                    "created_at": created_at,
                    "is_active": True
                }
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    logger.warning(f"User already exists: {email}")
                    return None
                raise

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email = ?",
                (email.lower(),)
            )
            row = cursor.fetchone()
            if row:
                user = dict(row)
                user['is_active'] = bool(user.get('is_active', 1))
                return user
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                user = dict(row)
                user['is_active'] = bool(user.get('is_active', 1))
                return user
            return None

    def update_last_login(self, user_id: str):
        """Update user's last login timestamp."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET last_login = ? WHERE user_id = ?
            """, (datetime.now().isoformat(), user_id))
            logger.debug(f"✓ Updated last login for user: {user_id}")

    def delete_user(self, user_id: str) -> bool:
        """Delete a user by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"✓ User deleted: {user_id}")
            return deleted

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (admin function)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, full_name, email, created_at, last_login, is_active FROM users")
            users = []
            for row in cursor.fetchall():
                user = dict(row)
                user['is_active'] = bool(user.get('is_active', 1))
                users.append(user)
            return users


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

# Single instance for the entire backend
db_manager = DatabaseManager()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_db() -> DatabaseManager:
    """Get the global database manager instance."""
    return db_manager
