from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp

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
        async with aiohttp.ClientSession() as session, session.get(str(url)):
            return True
    except aiohttp.ClientConnectorError:
        return False
