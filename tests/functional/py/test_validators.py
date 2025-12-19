from __future__ import annotations

import pytest

from clive.__private.py.exceptions import (
    InvalidNumberOfKeyPairsError,
    InvalidPageNumberError,
    InvalidPageSizeError,
)
from clive.__private.py.validators import (
    AccountNameValidator,
    KeyPairsNumberValidator,
    PageNumberValidator,
    PageSizeValidator,
)


class TestAccountNameValidator:
    def test_valid_account_name(self) -> None:
        """Test that valid account names pass validation."""
        validator = AccountNameValidator()
        validator.validate("alice")  # Should not raise

    def test_invalid_type_raises_type_error(self) -> None:
        """Test that non-string input raises TypeError."""
        validator = AccountNameValidator()
        with pytest.raises(TypeError, match="Expected str"):
            validator.validate(123)

    def test_none_raises_type_error(self) -> None:
        """Test that None input raises TypeError."""
        validator = AccountNameValidator()
        with pytest.raises(TypeError, match="Expected str"):
            validator.validate(None)


class TestPageNumberValidator:
    def test_valid_page_number(self) -> None:
        """Test that valid page numbers pass validation."""
        validator = PageNumberValidator()
        validator.validate(0)
        validator.validate(100)
        validator.validate(100000)

    def test_bool_rejected(self) -> None:
        """Test that bool is rejected even though isinstance(True, int) is True."""
        validator = PageNumberValidator()
        with pytest.raises(TypeError, match="Expected int"):
            validator.validate(True)  # noqa: FBT003
        with pytest.raises(TypeError, match="Expected int"):
            validator.validate(False)  # noqa: FBT003

    def test_negative_raises_error(self) -> None:
        """Test that negative page numbers raise InvalidPageNumberError."""
        validator = PageNumberValidator()
        with pytest.raises(InvalidPageNumberError):
            validator.validate(-1)

    def test_max_exceeded_raises_error(self) -> None:
        """Test that exceeding max page number raises InvalidPageNumberError."""
        validator = PageNumberValidator()
        with pytest.raises(InvalidPageNumberError):
            validator.validate(100001)

    def test_string_raises_type_error(self) -> None:
        """Test that string input raises TypeError."""
        validator = PageNumberValidator()
        with pytest.raises(TypeError, match="Expected int"):
            validator.validate("1")


class TestPageSizeValidator:
    def test_valid_page_size(self) -> None:
        """Test that valid page sizes pass validation."""
        validator = PageSizeValidator()
        validator.validate(1)
        validator.validate(100)
        validator.validate(1000)

    def test_bool_rejected(self) -> None:
        """Test that bool is rejected."""
        validator = PageSizeValidator()
        with pytest.raises(TypeError, match="Expected int"):
            validator.validate(True)  # noqa: FBT003

    def test_zero_raises_error(self) -> None:
        """Test that zero page size raises InvalidPageSizeError."""
        validator = PageSizeValidator()
        with pytest.raises(InvalidPageSizeError):
            validator.validate(0)

    def test_max_exceeded_raises_error(self) -> None:
        """Test that exceeding max page size raises InvalidPageSizeError."""
        validator = PageSizeValidator()
        with pytest.raises(InvalidPageSizeError):
            validator.validate(1001)


class TestKeyPairsNumberValidator:
    def test_valid_number(self) -> None:
        """Test that valid numbers pass validation."""
        validator = KeyPairsNumberValidator()
        validator.validate(1)
        validator.validate(10)
        validator.validate(100)

    def test_bool_rejected(self) -> None:
        """Test that bool is rejected."""
        validator = KeyPairsNumberValidator()
        with pytest.raises(TypeError, match="Expected int"):
            validator.validate(True)  # noqa: FBT003

    def test_zero_raises_error(self) -> None:
        """Test that zero raises error."""
        validator = KeyPairsNumberValidator()
        with pytest.raises(InvalidNumberOfKeyPairsError):
            validator.validate(0)
