"""
CarePath AI — Authentication Service
=====================================
Handles user registration (with hashed passwords) and login (with secure verification).
Never stores or logs plaintext passwords.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from database.crud import user_crud
from database.models import User

# Import hashing helpers — try backend path first, then root-level fallback
try:
    from app.core.security import get_password_hash, verify_password
except ImportError:
    from backend.app.core.security import get_password_hash, verify_password



def register_user(session: Session, email: str, plaintext_password: str) -> User:
    """
    Register a new user.

    The password is hashed before storage — plaintext is never persisted.
    """
    hashed = get_password_hash(plaintext_password)
    user_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    return user_crud.create_user(
        session=session,
        user_id=user_id,
        email=email,
        password_hash=hashed,
        role="patient",
        account_status="active",
        created_at=now,
        updated_at=now,
    )


def authenticate_user(session: Session, email: str, password_input: str) -> Optional[User]:
    """
    Authenticate a user by email and plaintext password.

    Returns the User model on success, None on failure.
    Never compares passwords in plaintext — always uses the PBKDF2 verifier.
    """
    user = user_crud.get_user_by_email(session, email)

    # Tolerate common typo where '.' and ',' are swapped in email
    if not user and "," in email:
        user = user_crud.get_user_by_email(session, email.replace(",", "."))

    if not user:
        return None

    # Constant-time hash comparison — no plaintext fallback
    if not verify_password(password_input, user.password_hash):
        return None

    return user


def get_user_profile(session: Session, user_id) -> Optional[User]:
    """Retrieve a user by ID."""
    return user_crud.get_user(session, user_id)
