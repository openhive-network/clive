from __future__ import annotations

from typing import TYPE_CHECKING, Any

from clive.exceptions import CliveError, CommunicationError

if TYPE_CHECKING:
    from clive.__private.models.schemas import JSONRPCRequest
    from clive.exceptions import CommunicationResponseT


class BeekeeperError(CliveError):
    """Base class for Beekeeper errors."""


class BeekeeperTimeoutError(BeekeeperError):
    pass


class BeekeeperTokenNotAvailableError(BeekeeperError):
    pass


class BeekeeperNotConfiguredError(BeekeeperError):
    pass


class BeekeeperUrlNotSetError(BeekeeperNotConfiguredError):
    pass


class BeekeeperNotificationServerNotConfiguredError(BeekeeperNotConfiguredError):
    pass


class BeekeeperNon200StatusCodeError(BeekeeperError):
    pass


class BeekeeperAlreadyRunningError(BeekeeperError):
    pass


class BeekeeperNotRunningError(BeekeeperError):
    pass


class BeekeeperDidNotClosedError(BeekeeperError):
    pass


class BeekeeperNonZeroExitCodeError(BeekeeperError):
    pass


class BeekeeperNotificationServerNotSetError(BeekeeperError):
    pass


class BeekeeperResponseError(BeekeeperError, CommunicationError):
    def __init__(self, url: str, request: JSONRPCRequest, response: CommunicationResponseT | None = None) -> None:
        super().__init__(url, request.json(by_alias=True), response)


class BeekeeperNotMatchingIdJsonRPCError(BeekeeperError):
    def __init__(self, given: Any, got: Any) -> None:  # noqa: ANN401
        self.given = given
        self.got = got
        message = f"Given id `{given}` does not match the id of the response `{got}`"
        super().__init__(message)
