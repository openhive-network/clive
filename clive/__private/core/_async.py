from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, TypeVar

from clive.__private.core._thread import thread_pool

if TYPE_CHECKING:
    from collections.abc import Coroutine

T = TypeVar("T")


def asyncio_run(coroutine: Coroutine[Any, Any, T]) -> T:
    """
    Make the coroutine run, even if there is an event loop running (like by using nest_asyncio).

    Inspired by: https://github.com/jupyter/nbclient/pull/113
    """
    return thread_pool.submit(asyncio.run, coroutine).result()
