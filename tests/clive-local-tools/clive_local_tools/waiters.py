from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


async def wait_for(condition: Callable[[], bool], message: str | Callable[[], str], timeout: float = 10.0) -> None:
    async def __wait_for() -> None:
        while not condition():
            await asyncio.sleep(0.1)

    try:
        await asyncio.wait_for(__wait_for(), timeout=timeout)
    except asyncio.TimeoutError:
        message_ = message if isinstance(message, str) else message()
        raise AssertionError(f"{message_}, wait_for timeout is {timeout:.2f}") from None
