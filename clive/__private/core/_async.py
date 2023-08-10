from __future__ import annotations

import asyncio
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
