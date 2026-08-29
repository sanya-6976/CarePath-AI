import os
import pytest
from src.config import settings


def is_allowed_file_extension(filename: str) -> bool:
    """Helper to validate file extensions against settings."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in settings.ALLOWED_UPLOAD_EXTENSIONS


def is_allowed_file_size(size_bytes: int) -> bool:
    """Helper to validate file size against settings."""
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    return size_bytes <= max_bytes


def test_allowed_upload_extensions():
    """Test validation of allowed and forbidden upload extensions."""
    assert is_allowed_file_extension("report.pdf") is True
    assert is_allowed_file_extension("skin_lesion.jpg") is True
    assert is_allowed_file_extension("scan.jpeg") is True
    assert is_allowed_file_extension("lab.png") is True
    assert is_allowed_file_extension("notes.txt") is True

    # Bad extensions
    assert is_allowed_file_extension("malware.exe") is False
    assert is_allowed_file_extension("script.sh") is False
    assert is_allowed_file_extension("hack.py") is False


def test_allowed_upload_file_size():
    """Test validation of file size limits."""
    small_file = 5 * 1024 * 1024  # 5 MB
    large_file = 15 * 1024 * 1024 # 15 MB (exceeds 10 MB limit)

    assert is_allowed_file_size(small_file) is True
    assert is_allowed_file_size(large_file) is False
