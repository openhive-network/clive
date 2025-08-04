from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from pathlib import Path


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


class NotRelativePathError(CliveError):
    """
    Raised when a path is not relative to the expected root path.

    Args:
        whole_path: The full path that is expected to be relative.
        root_path: The root path against which the relative check is made.
    """

    def __init__(self, whole_path: str | Path, root_path: str | Path) -> None:
        message = f"The whole_path {whole_path} is not relative to the root_path {root_path}."
        super().__init__(message)
