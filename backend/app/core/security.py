"""
CarePath AI — JWT & Security Utilities
========================================
Provides:
  - Real PBKDF2 password hashing / verification (stdlib, no bcrypt dependency)
  - Real HS256-signed JWT creation and validation via PyJWT
  - PHI redaction utility
  - get_current_user FastAPI dependency (Bearer token extraction + DB lookup)
  - verify_patient_ownership authorization guard

All secrets are loaded from environment variables — never hardcoded.

NOTE: This module reads from os.environ directly to avoid ambiguous dual-config
      path collision between root app/core/config.py and backend/app/core/config.py.
"""

import hashlib
import hmac
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session


# ── Runtime config helpers (read from os.environ) ────────────────────────────

def _secret_key() -> str:
    secret = os.environ.get("JWT_SECRET_KEY") or os.environ.get("SECRET_KEY")
    if not secret or secret.startswith("REPLACE_WITH_") or len(secret) < 32:
        raise RuntimeError("JWT_SECRET_KEY must be configured with a random value of at least 32 characters.")
    return secret

def _algorithm() -> str:
    return os.environ.get("ALGORITHM", "HS256")

def _expire_minutes() -> int:
    try:
        return int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    except (TypeError, ValueError):
        return 60

def _salt() -> bytes:
    s = os.environ.get("PASSWORD_SALT")
    if not s or s.startswith("REPLACE_WITH_") or len(s) < 16:
        raise RuntimeError("PASSWORD_SALT must be configured with a random value of at least 16 characters.")
    return s.encode("utf-8")


# ── PHI Redaction ─────────────────────────────────────────────────────────────

class PHIRedactor:
    """Sanitize Protected Health Information from text before logging."""
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    PHONE_PATTERN = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")
    EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    MRN_PATTERN = re.compile(r"\bMRN\d{8}\b")

    @classmethod
    def redact(cls, text: str) -> str:
        if not text:
            return ""
        text = cls.SSN_PATTERN.sub("[REDACTED_SSN]", text)
        text = cls.PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
        text = cls.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
        text = cls.MRN_PATTERN.sub("[REDACTED_MRN]", text)
        return text


# ── Password Hashing ──────────────────────────────────────────────────────────

def get_password_hash(password: str) -> str:
    """PBKDF2-HMAC-SHA256, 200 000 rounds (NIST 2024 recommended minimum)."""
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), _salt(), 200_000)
    return key.hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    return hmac.compare_digest(get_password_hash(plain_password), hashed_password)


# ── JWT ───────────────────────────────────────────────────────────────────────

def _jwt():
    try:
        import jwt as _jwt_lib
        return _jwt_lib
    except ImportError:
        raise RuntimeError("PyJWT is required. Run: pip install PyJWT")


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Issue a signed HS256 JWT embedding the user_id as the 'sub' claim.
    Returns a real JWT string — three base64url segments separated by dots.
    """
    try:
        jwt = _jwt()
    except RuntimeError:
        raise
    delta = expires_delta or timedelta(minutes=_expire_minutes())
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "exp": now + delta,
        "iat": now,
        "type": "access",
    }
    return jwt.encode(payload, _secret_key(), algorithm=_algorithm())


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode + validate JWT. Raises HTTP 401 on failure.
    """
    try:
        jwt = _jwt()
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication service is not configured.")
    try:
        return jwt.decode(token, _secret_key(), algorithms=[_algorithm()])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── FastAPI DB dependency (deferred import to avoid circular) ─────────────────

def _db_dep():
    from database.connections import get_db
    yield from get_db()


# ── FastAPI Auth Dependency ───────────────────────────────────────────────────

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(_db_dep),
):
    """
    Reusable FastAPI dependency.

    1. Extracts Bearer token from the Authorization header.
    2. Validates JWT signature + expiration (raises 401 on failure).
    3. Looks up the user in the database (raises 401 if not found).
    4. Returns the authenticated User SQLAlchemy model instance.
    """
    from database.models import User

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)

    user_id_str: Optional[str] = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token: missing subject claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token: invalid user identifier.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.user_id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if getattr(user, "account_status", "active") not in ("active", None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or deactivated.",
        )

    return user


# ── Authorization Guard ───────────────────────────────────────────────────────

def verify_patient_ownership(current_user, patient_id: str) -> None:
    """
    Enforce that the authenticated user owns the requested patient_id.

    Raises HTTP 400 for malformed UUIDs.
    Raises HTTP 403 if the patient_id does not match current_user.user_id.

    Usage in an endpoint:
        verify_patient_ownership(current_user, req.patient_id)
    """
    try:
        requested_uuid = uuid.UUID(patient_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid patient_id format.",
        )

    if requested_uuid != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you are not authorized to access this patient's data.",
        )


def verify_resource_ownership(current_user, resource_user_id) -> None:
    """Reject cross-patient access after a resource has been resolved."""
    if resource_user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: you are not authorized to access this patient's data.")


def require_admin(current_user) -> None:
    if str(getattr(current_user, "role", "")).lower() not in {"admin", "clinician"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This operation requires an authorized care-team role.")
