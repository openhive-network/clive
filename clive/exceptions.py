from __future__ import annotations

from abc import ABC
from typing import ClassVar

from clive.__private.cli.completion import is_tab_completion_active

if not is_tab_completion_active():
    pass


class CliveError(Exception):
    """Base class for all clive exceptions."""


class CliveDeveloperError(Exception):
    """Base class for all clive developer exceptions."""


class KnownError(CliveError, ABC):
    """
    A CliveError that stores the error message that is known to be raised by some external service.

    All errors of this type should define `ERROR_MESSAGE` class variable.
    """

    ERROR_MESSAGE: ClassVar[str]


class NoItemSelectedError(CliveError):
    """Raised when tried to access `selected` property of Select widget when no item was selected."""


class ScreenError(CliveError):
    """Base class for all screen exceptions."""


class ScreenNotFoundError(ScreenError):
    """Raised when screen is not found."""


class CannotUnlockError(CliveError):
    pass


class TransactionNotSignedError(CliveError):
    pass


class RequestIdError(CliveError):
    """Raise when quantity of request_ids is greater than 100."""
