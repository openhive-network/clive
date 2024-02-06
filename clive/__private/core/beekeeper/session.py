from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.beekeeper.api_session import BeekeeperApiSession

if TYPE_CHECKING:
    from clive.core.url import Url

"""
Very draft

This will be based on helpy and separate for both Async and Synch version.

"""


class BeekeeperSession:
    def __init__(self, http_endpoint: Url, notification_endpoint: Url) -> None:
        self.token: str | None = None
        self.http_endpoint: Url = http_endpoint
        self.notification_endpoint: Url = notification_endpoint
        self.api = BeekeeperApiSession(owner=self)

    async def init_session(self) -> None:
        """Create session and retrieve session token to use."""
        assert not self.token, "Session already set."
        self.token = (
            await self.api.create_session(
                notifications_endpoint=self.notification_endpoint.as_string(with_protocol=False),
                salt=str(id(self)),
            )
        ).token

    async def close_session(self) -> None:
        """Close current session."""
        assert self.token, "Session needs to be set first."
        await self.api.close_session()
