"""Tests for Shared Input Validation Helpers (app/core/validation.py).

Validates:
- validate_image_bytes: empty bytes, oversized bytes, valid bytes.
- validate_text_input: empty string, whitespace-only, too long, valid.
- validate_top_k: below min, above max, non-integer, valid.
"""
import pytest

from app.core.validation import validate_image_bytes, validate_text_input, validate_top_k
from app.core.exceptions import InputValidationError


# ---------------------------------------------------------------------------
# validate_image_bytes
# ---------------------------------------------------------------------------

class TestValidateImageBytes:

    def test_empty_bytes_raises(self):
        with pytest.raises(InputValidationError, match="empty"):
            validate_image_bytes(b"")

    def test_none_like_falsy_bytes_raises(self):
        with pytest.raises(InputValidationError):
            validate_image_bytes(bytes())

    def test_oversized_raises(self):
        # 21 MB — just above the 20 MB default limit
        oversized = b"x" * (21 * 1024 * 1024)
        with pytest.raises(InputValidationError, match="exceeds"):
            validate_image_bytes(oversized, max_mb=20)

    def test_exactly_at_limit_passes(self):
        # Exactly 20 MB is within limit
        at_limit = b"x" * (20 * 1024 * 1024)
        validate_image_bytes(at_limit, max_mb=20)  # Should not raise

    def test_small_valid_bytes_pass(self):
        validate_image_bytes(b"PNG_HEADER_BYTES", max_mb=5)  # Should not raise

    def test_custom_limit(self):
        one_mb = b"y" * (1 * 1024 * 1024)
        with pytest.raises(InputValidationError):
            validate_image_bytes(one_mb, max_mb=0)  # 0 MB limit → any payload fails


# ---------------------------------------------------------------------------
# validate_text_input
# ---------------------------------------------------------------------------

class TestValidateTextInput:

    def test_empty_string_raises(self):
        with pytest.raises(InputValidationError):
            validate_text_input("")

    def test_whitespace_only_raises(self):
        with pytest.raises(InputValidationError, match="1 character"):
            validate_text_input("   ")

    def test_too_long_raises(self):
        long_text = "a" * 32_769
        with pytest.raises(InputValidationError, match="exceeds"):
            validate_text_input(long_text)

    def test_exactly_max_length_passes(self):
        max_text = "a" * 32_768
        validate_text_input(max_text)  # Should not raise

    def test_valid_short_text_passes(self):
        validate_text_input("Patient presents with cough.")

    def test_custom_min_len(self):
        with pytest.raises(InputValidationError):
            validate_text_input("ab", min_len=5)

    def test_non_string_raises(self):
        with pytest.raises(InputValidationError):
            validate_text_input(12345)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# validate_top_k
# ---------------------------------------------------------------------------

class TestValidateTopK:

    def test_below_minimum_raises(self):
        with pytest.raises(InputValidationError, match="between 1 and 10"):
            validate_top_k(0)

    def test_above_maximum_raises(self):
        with pytest.raises(InputValidationError, match="between 1 and 10"):
            validate_top_k(11)

    def test_non_integer_raises(self):
        with pytest.raises(InputValidationError, match="integer"):
            validate_top_k(2.5)  # type: ignore[arg-type]

    def test_string_raises(self):
        with pytest.raises(InputValidationError):
            validate_top_k("3")  # type: ignore[arg-type]

    def test_valid_values_pass(self):
        for k in range(1, 11):
            validate_top_k(k)  # Should not raise

    def test_custom_range(self):
        validate_top_k(5, min_k=1, max_k=5)
        with pytest.raises(InputValidationError):
            validate_top_k(6, min_k=1, max_k=5)


# ---------------------------------------------------------------------------
# Exception attributes
# ---------------------------------------------------------------------------

class TestInputValidationErrorAttributes:

    def test_error_code_is_correct(self):
        try:
            validate_image_bytes(b"")
        except InputValidationError as exc:
            assert exc.error_code == "input_validation_error"
            assert isinstance(exc.message, str)
            assert len(exc.message) > 0
