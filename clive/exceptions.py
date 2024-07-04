from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeAlias

from clive.__private.abstract_class import AbstractClass
from clive.__private.cli.completion import is_tab_completion_active

if not is_tab_completion_active():
    from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.notification_http_server import JsonT

    CommunicationResponseT: TypeAlias = str | JsonT | list[JsonT]


class CliveError(Exception):
    """Base class for all clive exceptions."""


class CliveDeveloperError(Exception):
    """Base class for all clive developer exceptions."""


class KnownError(CliveError, AbstractClass):
    """
    A CliveError that stores the error message that is known to be raised by some external service.

    All errors of this type should define `ERROR_MESSAGE` class variable.
    """

    ERROR_MESSAGE: ClassVar[str]


class CommunicationError(CliveError):
    """Base class for all communication exceptions."""

    def __init__(
        self, url: str, request: str, response: CommunicationResponseT | None = None, *, message: str = ""
    ) -> None:
        self.url = url
        self.request = request
        self.response = response
        message = message or self.__create_message()
        logger.error(message)
        super().__init__(message)

    @property
    def is_response_available(self) -> bool:
        return self.get_response() is not None

    def get_response_error_messages(self) -> list[str]:
        result = self.get_response()
        if result is None:
            return []

        if isinstance(result, dict):
            message = result.get("error", {}).get("message", None)
            return [str(message)] if message is not None else []

        messages = []
        for item in result:
            message = item.get("error", {}).get("message", None)
            if message is not None:
                messages.append(str(message))
        return messages

    def get_response(self) -> JsonT | list[JsonT] | None:
        return self.response if isinstance(self.response, dict | list) else None

    def _get_reply(self) -> str:
        if (result := self.get_response()) is not None:
            return f"{result=}"

        if self.response is not None:
            return f"response={self.response}"

        return "no response available"

    def __create_message(self) -> str:
        return (
            f"Problem occurred during communication with: url={self.url}, request={self.request}, {self._get_reply()}"
        )


class UnknownResponseFormatError(CommunicationError):
    """Raised when the response format is unknown."""

    def __init__(self, url: str, request: str, response: CommunicationResponseT | None = None) -> None:
        self.url = url
        self.request = request
        self.response = response
        message = f"Unknown response format from: {url=}, {request=}, {self._get_reply()}"
        super().__init__(url, request, response, message=message)


class CommunicationTimeoutError(CommunicationError):
    def __init__(self, url: str, request: str, timeout: float, attempts: int) -> None:
        self.url = url
        self.request = request
        self.timeout = timeout
        self.attempts = attempts
        message = (
            f"Timeout occurred during communication with: {url=}. Exceeded {attempts} attempts, each of {timeout:.2f}s."
        )
        super().__init__(url, request, message=message)


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
