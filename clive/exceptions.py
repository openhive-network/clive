from __future__ import annotations

from typing import Final


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
