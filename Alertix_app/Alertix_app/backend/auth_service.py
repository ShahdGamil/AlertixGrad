"""
Authentication Service for Alertix
===================================
Handles JWT token generation, password hashing, and user authentication.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid
import hashlib
import secrets

# Try to import JWT library
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("⚠️ PyJWT not installed. Run: pip install PyJWT")

# Try to import bcrypt
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    print("⚠️ bcrypt not installed. Run: pip install bcrypt")

from config import (
    JWT_SECRET_KEY,
    JWT_ACCESS_TOKEN_EXPIRE_HOURS,
    JWT_ALGORITHM,
    PASSWORD_MIN_LENGTH
)

logger = logging.getLogger(__name__)


class AuthService:
    """Handles authentication operations."""

    def __init__(self):
        self.secret_key = JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM
        self.token_expire_hours = JWT_ACCESS_TOKEN_EXPIRE_HOURS

    # ============================================================================
    # PASSWORD HASHING
    # ============================================================================

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Falls back to SHA-256 if bcrypt is not available.
        """
        if BCRYPT_AVAILABLE:
            # Use bcrypt (recommended)
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
        else:
            # Fallback to SHA-256 with salt (less secure)
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return f"sha256:{salt}:{password_hash}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        """
        if password_hash.startswith("sha256:"):
            # SHA-256 fallback verification
            parts = password_hash.split(":")
            if len(parts) != 3:
                return False
            salt = parts[1]
            stored_hash = parts[2]
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == stored_hash
        elif BCRYPT_AVAILABLE:
            # bcrypt verification
            try:
                password_bytes = password.encode('utf-8')
                hash_bytes = password_hash.encode('utf-8')
                return bcrypt.checkpw(password_bytes, hash_bytes)
            except Exception as e:
                logger.error(f"Password verification error: {e}")
                return False
        else:
            logger.error("Cannot verify password - bcrypt not available and hash is not SHA-256 format")
            return False

    def validate_password(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
        return True, ""

    # ============================================================================
    # JWT TOKEN HANDLING
    # ============================================================================

    def create_access_token(
        self,
        user_id: str,
        email: str,
        full_name: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        """
        if not JWT_AVAILABLE:
            raise RuntimeError("PyJWT is not installed. Run: pip install PyJWT")

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=self.token_expire_hours)

        payload = {
            "sub": user_id,  # Subject (user ID)
            "email": email,
            "name": full_name,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.

        Returns:
            Decoded payload if valid, None if invalid
        """
        if not JWT_AVAILABLE:
            logger.error("PyJWT is not installed")
            return None

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def get_user_from_token(self, token: str) -> Optional[Dict[str, str]]:
        """
        Extract user info from a valid token.

        Returns:
            Dict with user_id, email, name if valid, None if invalid
        """
        payload = self.verify_token(token)
        if payload:
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "full_name": payload.get("name")
            }
        return None

    # ============================================================================
    # USER ID GENERATION
    # ============================================================================

    @staticmethod
    def generate_user_id() -> str:
        """Generate a unique user ID."""
        return str(uuid.uuid4())


# Global instance
auth_service = AuthService()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password."""
    return auth_service.hash_password(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return auth_service.verify_password(password, password_hash)


def create_access_token(user_id: str, email: str, full_name: str) -> str:
    """Create a JWT access token."""
    return auth_service.create_access_token(user_id, email, full_name)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    return auth_service.verify_token(token)


def get_user_from_token(token: str) -> Optional[Dict[str, str]]:
    """Extract user info from a token."""
    return auth_service.get_user_from_token(token)


def generate_user_id() -> str:
    """Generate a unique user ID."""
    return AuthService.generate_user_id()


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    return auth_service.validate_password(password)
