from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine


async def wait_for(
    condition: Callable[[], bool | Coroutine[Any, Any, bool]],
    message: str | Callable[[], str],
    timeout: float = 10.0,
) -> None:
    """
    Wait for a condition to be true.

    It supports both synchronous and asynchronous conditions.
    """

    async def __wait_for() -> None:
        while True:
            if asyncio.iscoroutinefunction(condition):
                result = await condition()
            else:
                result = condition()
            if result:
                break
            await asyncio.sleep(0.1)

    try:
        await asyncio.wait_for(__wait_for(), timeout=timeout)
    except TimeoutError:
        message_ = message if isinstance(message, str) else message()
        raise AssertionError(f"{message_}, wait_for timeout is {timeout:.2f}") from None
