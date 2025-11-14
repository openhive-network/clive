from __future__ import annotations

from typing import Any, Final


class CliveError(Exception):
    """Base class for all clive exceptions."""


class CliveDeveloperError(Exception):
    """Base class for all clive developer exceptions."""


class NoItemSelectedError(CliveError):
    """Raised when tried to access `selected` property of Select widget when no item was selected."""


class ScreenError(CliveError):
    """Base class for all screen exceptions."""


class ScreenNotFoundError(ScreenError):
    """Raised when screen is not found."""


class TransactionNotSignedError(CliveError):
    """
    Raise when trying to broadcast unsigned transaction.

    Attributes:
        MESSAGE: Error message to be displayed.
    """

    MESSAGE: Final[str] = "Could not broadcast unsigned transaction."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class RequestIdError(CliveError):
    """Raise when quantity of request_ids is greater than 100."""


class ProfileNotLoadedError(CliveError):
    """Raise when profile is requested and was not loaded."""


class WrongTypeError(CliveError):
    """
    Raised when the type of the value is not the expected one.

    Args:
        expected_type: Expected type.
        actual_type: Actual type.
    """

    def __init__(self, expected_type: type[Any], actual_type: type[Any]) -> None:
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.message = f"Expected type {expected_type}, got {actual_type}"
        super().__init__(self.message)
