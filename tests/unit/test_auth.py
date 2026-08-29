import pytest
from backend.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_password_hashing_and_verification():
    """Test Argon2/Bcrypt password hashing and validation."""
    password = "SecurePatientPass2026!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPass", hashed) is False


def test_jwt_access_token_creation_and_decoding():
    """Test JWT access token encoding, payload extraction, and validation."""
    sub = "user_uuid_998877"
    token = create_access_token(subject=sub)
    
    assert isinstance(token, str)
    payload = decode_access_token(token)
    assert payload["sub"] == sub
    assert payload["type"] == "access"


def test_invalid_jwt_decoding_raises_error():
    """Test that corrupted JWT token raises ValueError."""
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalidpayload.invalid signature"
    with pytest.raises(ValueError, match="Invalid or expired JWT token"):
        decode_access_token(invalid_token)
