"""Exceptions for the PY module."""

from __future__ import annotations


class PyError(Exception):
    """Base exception for all PY module errors."""


class PyValidationError(PyError):
    """Base exception for validation errors."""


class PyContextManagerNotUsedError(PyError):
    """Raised when UnlockedClivePy is used without async context manager."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class PasswordRequirementsNotMetError(PyValidationError):
    """Raised when the provided password does not meet the requirements."""

    def __init__(self, description: str) -> None:
        super().__init__(f"Password requirements not met: {description}")


class InvalidAccountNameError(PyValidationError):
    """Raised when the provided account name is invalid."""

    def __init__(self, account_name: str, description: str | None = None) -> None:
        message = f"Invalid account name: '{account_name}'."
        if description:
            message = f"{message} {description}"
        super().__init__(message)
        self.account_name = account_name
        self.description = description


class InvalidProfileNameError(PyValidationError):
    """Raised when the provided profile name is invalid."""

    def __init__(self, profile_name: str, description: str) -> None:
        super().__init__(f"Invalid profile name: '{profile_name}'. {description}")


class InvalidPageNumberError(PyValidationError):
    """Raised when the provided page number is invalid."""

    def __init__(self, page_number: int, min_number: int = 0, max_number: int | None = None) -> None:
        if max_number is not None:
            message = (
                f"Invalid page number: {page_number}. "
                f"Page number must be between {min_number} and {max_number}."
            )
        else:
            message = f"Invalid page number: {page_number}. Page number must be greater or equal to {min_number}."
        super().__init__(message)


class InvalidPageSizeError(PyValidationError):
    """Raised when the provided page size is invalid."""

    def __init__(self, page_size: int, min_size: int, max_size: int | None = None) -> None:
        if max_size is not None:
            message = (
                f"Invalid page size: {page_size}. "
                f"Page size must be between {min_size} and {max_size}."
            )
        else:
            message = f"Invalid page size: {page_size}. Page size must be greater than or equal to {min_size}."
        super().__init__(message)


class InvalidNumberOfKeyPairsError(PyValidationError):
    """Raised when the provided number of key pairs is invalid."""

    def __init__(self, number_of_key_pairs: int, min_size: int) -> None:
        super().__init__(
            f"Invalid number of key pairs: {number_of_key_pairs}. "
            f"Number of key pairs must be greater than or equal to {min_size}."
        )


class InvalidAuthorityTypeError(PyValidationError):
    """Raised when the provided authority type is invalid."""

    def __init__(self, authority: str, valid_authorities: frozenset[str]) -> None:
        valid_str = ", ".join(sorted(valid_authorities))
        super().__init__(f"Invalid authority type: '{authority}'. Valid authorities are: {valid_str}.")


class AccountNotFoundError(PyError):
    """Raised when the specified account does not exist on the blockchain."""

    def __init__(self, account_name: str) -> None:
        super().__init__(f"Account '{account_name}' not found on the blockchain.")
        self.account_name = account_name
