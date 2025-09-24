from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy.communication import get_communicator_cls
from beekeepy.exceptions import CommunicationError
from beekeepy.handle.settings import RemoteHandleSettings

if TYPE_CHECKING:
    from beekeepy.interfaces import HttpUrl


async def is_url_reachable(url: HttpUrl) -> bool:
    """
    Check if the given url is reachable.

    Args:
        url: The URL to check.

    Returns:
        True if the URL is reachable, False otherwise.
    """
    try:
        s = RemoteHandleSettings()
        c = get_communicator_cls()(settings=s)
        await c.async_get(url=url)
    except CommunicationError:
        return False

    return True
