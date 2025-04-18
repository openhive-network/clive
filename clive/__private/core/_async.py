from __future__ import annotations

import asyncio
import contextlib
from typing import TYPE_CHECKING, TypeVar

from clive.__private.core._thread import thread_pool

if TYPE_CHECKING:
    from collections.abc import Awaitable

T = TypeVar("T")


def asyncio_run(awaitable: Awaitable[T]) -> T:
    """
    Make the coroutine run, even if there is an event loop running (like by using nest_asyncio).

    Inspired by: https://github.com/jupyter/nbclient/pull/113
    """

    async def await_for_given_awaitable() -> T:
        return await awaitable

    return thread_pool.submit(asyncio.run, await_for_given_awaitable()).result()


async def event_wait(event: asyncio.Event, timeout: float | None = None) -> bool:  # noqa: ASYNC109
    # suppress TimeoutError because we'll return False in case of timeout
    with contextlib.suppress(asyncio.TimeoutError):
        await asyncio.wait_for(event.wait(), timeout)
    return event.is_set()
