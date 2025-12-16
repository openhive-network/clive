"""Exceptions for the PY module."""

from __future__ import annotations


class PyContextManagerNotUsedError(Exception):
    """Raised when UnlockedClivePy is used without async context manager."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class PasswordRequirementsNotMetError(Exception):
    """Raised when the provided password does not meet the requirements."""

    def __init__(self, description: str) -> None:
        super().__init__(f"Password requirements not met: {description}")


class InvalidAccountNameError(Exception):
    """Raised when the provided account name is invalid."""

    def __init__(self, account_name: str) -> None:
        super().__init__(f"Invalid account name: '{account_name}'.")


class InvalidProfileNameError(Exception):
    """Raised when the provided profile name is invalid."""

    def __init__(self, profile_name: str, description: str) -> None:
        super().__init__(f"Invalid profile name: '{profile_name}'. {description}")


class InvalidPageNumberError(Exception):
    """Raised when the provided page number is invalid."""

    def __init__(self, page_number: int, min_number: int = 0) -> None:
        super().__init__(f"Invalid page number: {page_number}. Page number must be greater or equal to {min_number}.")


class InvalidPageSizeError(Exception):
    """Raised when the provided page size is invalid."""

    def __init__(self, page_size: int, min_size: int) -> None:
        super().__init__(f"Invalid page size: {page_size}. Page size must be greater than or equal to {min_size}.")


class InvalidNumberOfKeyPairsError(Exception):
    """Raised when the provided number of key pairs is invalid."""

    def __init__(self, number_of_key_pairs: int, min_size: int) -> None:
        super().__init__(
            f"Invalid number of key pairs: {number_of_key_pairs}. "
            f"Number of key pairs must be greater than or equal to {min_size}."
        )
