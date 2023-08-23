from __future__ import annotations

from json import JSONDecodeError
from typing import TYPE_CHECKING, Any

from clive.__private.logger import logger

if TYPE_CHECKING:
    import httpx

    from clive.__private.core.beekeeper.notification_http_server import JsonT


class CliveError(Exception):
    """Base class for all clive exceptions."""


class CommunicationError(CliveError):
    """Base class for all communication exceptions."""

    def __init__(
        self, url: str, request: str, response: httpx.Response | dict[str, Any] | None = None, *, message: str = ""
    ) -> None:
        self.url = url
        self.request = request
        self.response = response
        message = message or self.__create_message()
        logger.error(message)
        super().__init__(message)

    def get_response_error_message(self) -> str | None:
        result = self.get_response_json()
        if result is None:
            return None

        message = result.get("error", {}).get("message", None)
        return str(message) if message is not None else message

    def get_response_json(self) -> JsonT | None:
        if self.response is None:
            return None

        if isinstance(self.response, dict):
            return self.response

        try:
            return self.response.json()  # type: ignore[no-any-return]
        except JSONDecodeError:
            return None

    def _get_reply(self) -> str:
        if (result := self.get_response_json()) is not None:
            return f"{result=}"

        if self.response is not None:
            assert not isinstance(self.response, dict)  # mypy check
            return f"response={self.response.text}"

        return "no response available"

    def __create_message(self) -> str:
        return (
            f"Problem occurred during communication with: url={self.url}, request={self.request}, {self._get_reply()}"
        )


class UnknownResponseFormatError(CommunicationError):
    """Raised when the response format is unknown."""

    def __init__(self, url: str, request: str, response: httpx.Response | dict[str, Any]) -> None:
        self.response = response
        message = f"Unknown response format from: {url=}, {request=}, {self._get_reply()}"
        super().__init__(url, request, response, message=message)


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


class InputTooShortError(FormValidationError):
    def __init__(self, *, expected_length: int, given_value: str) -> None:
        super().__init__(
            f"Expected length of {expected_length}, but string of {len(given_value)} given", given_value=given_value
        )


class RepeatedPasswordIsDifferentError(FormValidationError):
    def __init__(self) -> None:
        super().__init__("Repeated password is different than original one")


class AliasAlreadyInUseFormError(FormValidationError):
    def __init__(self, alias: str) -> None:
        super().__init__(f"Alias `{alias}` is already in use.", given_value=alias)


class PrivateKeyAlreadyInUseError(FormValidationError):
    def __init__(self) -> None:
        super().__init__("Private key is already in use.")


class CannotActivateError(CliveError):
    pass


class TransactionNotSignedError(CliveError):
    pass
