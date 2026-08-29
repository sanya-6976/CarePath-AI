import pytest
from backend.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_password_hashing():
    """Verify password hashing and verification."""
    raw_pass = "CarePathSecret123!"
    hashed = get_password_hash(raw_pass)
    
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_lifecycle():
    """Verify JWT access token encoding and decoding."""
    user_id = "user_test_uuid_123"
    token = create_access_token(subject=user_id)
    
    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"
