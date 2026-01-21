from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine


async def wait_for(
    condition: Callable[[], bool | Coroutine[Any, Any, bool]],
    message: str | Callable[[], str],
    timeout: float = 10.0,  # noqa: ASYNC109
) -> None:
    """
    Wait for a condition to be true.

    It supports both synchronous and asynchronous conditions.
    """
    try:
        async with asyncio.timeout(timeout):
            while True:
                result = await condition() if asyncio.iscoroutinefunction(condition) else condition()
                if result:
                    return
                await asyncio.sleep(0.1)
    except TimeoutError:
        message_ = message if isinstance(message, str) else message()
        raise AssertionError(f"{message_}, wait_for timeout is {timeout:.2f}") from None
