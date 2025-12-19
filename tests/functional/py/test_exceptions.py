from __future__ import annotations

from clive.py import (
    InvalidAccountNameError,
    InvalidPageNumberError,
    InvalidPageSizeError,
    PyError,
    PyValidationError,
)


class TestExceptionHierarchy:
    def test_py_validation_error_inherits_from_py_error(self) -> None:
        """Test that PyValidationError is a subclass of PyError."""
        assert issubclass(PyValidationError, PyError)

    def test_invalid_account_name_inherits_from_validation_error(self) -> None:
        """Test that InvalidAccountNameError is a subclass of PyValidationError."""
        assert issubclass(InvalidAccountNameError, PyValidationError)

    def test_invalid_page_number_inherits_from_validation_error(self) -> None:
        """Test that InvalidPageNumberError is a subclass of PyValidationError."""
        assert issubclass(InvalidPageNumberError, PyValidationError)

    def test_invalid_page_size_inherits_from_validation_error(self) -> None:
        """Test that InvalidPageSizeError is a subclass of PyValidationError."""
        assert issubclass(InvalidPageSizeError, PyValidationError)

    def test_can_catch_all_validation_errors(self) -> None:
        """Test that we can catch all validation errors with PyValidationError."""
        try:
            raise InvalidAccountNameError("bad")
        except PyValidationError:
            pass  # Expected

    def test_can_catch_all_py_errors(self) -> None:
        """Test that we can catch all PY errors with PyError."""
        try:
            raise InvalidAccountNameError("bad")
        except PyError:
            pass  # Expected


class TestInvalidAccountNameError:
    def test_basic_message(self) -> None:
        """Test that exception message contains account name."""
        exc = InvalidAccountNameError("bad_name")
        assert "bad_name" in str(exc)

    def test_with_description(self) -> None:
        """Test that exception message contains description when provided."""
        exc = InvalidAccountNameError("bad_name", "Name is too long")
        assert "bad_name" in str(exc)
        assert "Name is too long" in str(exc)

    def test_attributes_accessible(self) -> None:
        """Test that account_name and description attributes are accessible."""
        exc = InvalidAccountNameError("test_account", "some reason")
        assert exc.account_name == "test_account"
        assert exc.description == "some reason"

    def test_description_none_by_default(self) -> None:
        """Test that description is None when not provided."""
        exc = InvalidAccountNameError("test_account")
        assert exc.description is None


class TestInvalidPageNumberError:
    def test_message_contains_page_number(self) -> None:
        """Test that exception message contains page number."""
        exc = InvalidPageNumberError(-1, 0, 100000)
        assert "-1" in str(exc)


class TestInvalidPageSizeError:
    def test_message_contains_page_size(self) -> None:
        """Test that exception message contains page size."""
        exc = InvalidPageSizeError(0, 1, 1000)
        assert "0" in str(exc)
