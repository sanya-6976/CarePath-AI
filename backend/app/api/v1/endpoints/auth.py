"""
CarePath AI — Authentication Endpoints
========================================
POST /api/v1/auth/login      — password authentication → signed JWT
POST /api/v1/auth/register   — new user registration with hashed password
GET  /api/v1/auth/profile    — returns the authenticated user's own profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services import auth_service
from app.core.security import create_access_token, get_current_user


def _get_db():
    from database.connections import get_db
    yield from get_db()


router = APIRouter(prefix="/auth", tags=["Auth"])



# ── Request / Response schemas ────────────────────────────────────────────────

class AuthLogin(BaseModel):
    email: str
    password: str


class AuthRegister(BaseModel):
    email: str
    password: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login")
def login(credentials: AuthLogin, db: Session = Depends(_get_db)):
    """
    Authenticate with email + password.

    Returns a signed HS256 JWT on success.
    Returns HTTP 401 on invalid credentials.
    """
    try:
        user = auth_service.authenticate_user(db, credentials.email, credentials.password)
    except Exception as db_err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service temporarily unavailable. Please try again.",
        )

    if not user:
        # Generic message — do not reveal whether the email exists
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=str(user.user_id))

    return {
        "token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.user_id),
            "email": user.email,
            "role": user.role,
        },
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(credentials: AuthRegister, db: Session = Depends(_get_db)):
    """
    Register a new patient account.

    Password is hashed before storage — never stored in plaintext.
    Returns HTTP 409 if the email is already registered.
    """
    # Check for duplicate email
    from database.crud import user_crud
    existing = user_crud.get_user_by_email(db, credentials.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    try:
        user = auth_service.register_user(db, credentials.email, credentials.password)
        db.commit()
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again.",
        )

    return {
        "message": "Account created successfully.",
        "user_id": str(user.user_id),
    }


@router.get("/profile")
def get_profile(current_user=Depends(get_current_user)):
    """
    Returns the authenticated user's own profile.
    Requires a valid Bearer token.
    """
    first_name = ""
    last_name = ""
    if current_user.profile:
        first_name = current_user.profile.first_name or ""
        last_name = current_user.profile.last_name or ""
    full_name = f"{first_name} {last_name}".strip() or current_user.email

    return {
        "id": str(current_user.user_id),
        "email": current_user.email,
        "name": full_name,
        "role": current_user.role,
    }
