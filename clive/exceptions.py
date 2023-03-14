from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import Response


class CliveError(Exception):
    """Base class for all clive exceptions."""


class NodeAddressError(CliveError):
    """Base class for all node address exceptions."""


class CommunicationError(CliveError):
    """Base class for all communication exceptions."""


class UnknownResponseFormatError(CommunicationError):
    """Raised when the response format is unknown."""

    def __init__(self, response: Response) -> None:
        self.response = response
        message = (
            f"Unknown response format from url={response.url}\n"
            f"data={response.request.content!r}, result={response.json()}"
        )
        super().__init__(message)
