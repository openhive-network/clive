"""Exceptions for the SI module."""

from __future__ import annotations

from typing import Final


class SIContextManagerNotUsedError(Exception):
    """Raised when UnlockedCliveSi is used without async context manager."""

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


class CannotAddOperationToSignedTransactionError(Exception):
    """Raised when trying to add an operation to an already signed transaction."""

    def __init__(self) -> None:
        super().__init__(
            "Cannot add operations to an already signed transaction. "
            "Use force_unsign=True parameter in the transaction() method to remove the signature first."
        )


class MissingFromFileOrFromObjectError(Exception):
    """Raised when neither from_file nor from_object is provided."""

    def __init__(self) -> None:
        super().__init__("Either from_file or from_object must be provided.")


class BothArgumentsFromFileOrFromObjectPrividedError(Exception):
    """Raised when both from_file and from_object are provided."""

    def __init__(self) -> None:
        super().__init__("Only one of from_file or from_object should be provided, not both.")


class WrongAlreadySignedModeAutoSignError(Exception):
    """
    Raises when trying to use autosign together with already_signed_mode that is not 'error'.

    Attributes:
        MESSAGE: A message to be shown to the user.
    """

    MESSAGE: Final[str] = (
        "Autosign cannot be used together with already-signed modes 'override' or 'multisign'. "
        "Please choose another already-signed mode or disable autosign."
    )

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class TransactionAlreadySignedError(Exception):
    """
    Raises when trying to sign a transaction that is already signed without proper already-signed-mode.

    Attributes:
        MESSAGE: A message to be shown to the user.
    """

    MESSAGE: Final[str] = (
        "You cannot sign a transaction that is already signed.\n"
        "Use 'already-signed-mode override' to override the existing signature(s) or "
        "'already-signed-mode multisign' to add an additional signature."
    )

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)
