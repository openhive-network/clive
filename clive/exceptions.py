from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from helpy.exceptions import CommunicationError as HelpyCommunicationError
from helpy.exceptions import CommunicationResponseT as HelpyCommunicationResponseT

from clive.__private.abstract_class import AbstractClass

if TYPE_CHECKING:
    from helpy import HttpUrl


JsonT = dict[str, Any] | str | int | list[Any]


class CliveError(Exception):
    """Base class for all clive exceptions."""


class KnownError(CliveError, AbstractClass):
    """
    A CliveError that stores the error message that is known to be raised by some external service.

    All errors of this type should define `ERROR_MESSAGE` class variable.
    """

    ERROR_MESSAGE: ClassVar[str]


CommunicationError = HelpyCommunicationError
CommunicationResponseT = HelpyCommunicationResponseT


class UnknownResponseFormatError(CommunicationError):
    """Raised when the response format is unknown."""

    def __init__(self, url: HttpUrl, request: str, response: CommunicationResponseT | None = None) -> None:
        super().__init__(
            url, request, response, message=f"Unknown response format from: {url=}, {request=}, {response=}"
        )


class CommunicationTimeoutError(CommunicationError):
    def __init__(self, url: HttpUrl, request: str, timeout: float, attempts: int) -> None:
        self.timeout = timeout
        self.attempts = attempts
        super().__init__(
            url,
            request,
            message=f"Timeout occurred during communication with: {url=}. Exceeded {attempts} attempts, each of {timeout:.2f}s.",
        )


class NoItemSelectedError(CliveError):
    """Raised when tried to access `selected` property of Select widget when no item was selected."""


class ScreenError(CliveError):
    """Base class for all screen exceptions."""


class ScreenNotFoundError(ScreenError):
    """Raised when screen is not found."""


class FormValidationError(CliveError):
    def __init__(self, reason: str, *, given_value: str | None = None) -> None:
        self.reason = reason
        self.given_value = given_value
        super().__init__()


class NodeAddressError(FormValidationError):
    """Base class for all node address exceptions."""


class CannotActivateError(CliveError):
    pass


class TransactionNotSignedError(CliveError):
    pass


class RequestIdError(CliveError):
    """Raise when quantity of request_ids is greater than 100."""
