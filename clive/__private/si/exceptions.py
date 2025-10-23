"""Exceptions for the SI module."""

from __future__ import annotations


class InvalidPasswordLengthError(Exception):
    """Raised when the provided password length is invalid."""

    def __init__(self, min_length: int, max_length: int, current_length: int) -> None:
        super().__init__(
            f"Invalid password length: Current: {current_length}. Must be between {min_length} and {max_length} characters."
        )


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

    def __init__(self, page_number: int, min_number: int) -> None:
        super().__init__(f"Invalid page number: {page_number}. Page number must be greater or equal to 0.")


class InvalidPageSizeError(Exception):
    """Raised when the provided page size is invalid."""

    def __init__(self, page_size: int, min_size: int) -> None:
        super().__init__(f"Invalid page size: {page_size}. Page size must be greater than {min_size}.")


class InvalidNumberOfKeyPairsError(Exception):
    """Raised when the provided number of key pairs is invalid."""

    def __init__(self, number_of_key_pairs: int) -> None:
        super().__init__(
            f"Invalid number of key pairs: {number_of_key_pairs}. Number of key pairs must be greater than 0."
        )


class InvalidAuthorityLevelError(Exception):
    """Raised when the provided authority level is invalid."""

    def __init__(self, authority_level: str, valid_levels: list[str]) -> None:
        valid_levels_str = "', '".join(valid_levels)
        super().__init__(
            f"Invalid authority level: '{authority_level}'. Valid authority levels are: '{valid_levels_str}'."
        )


class InvalidPrivateKeyError(Exception):
    """Raised when the provided private key is invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid private key format.")
