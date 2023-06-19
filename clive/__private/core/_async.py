from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Coroutine
    from concurrent.futures import ThreadPoolExecutor


def asyncio_run(coroutine: Coroutine[Any, Any, Any], pool: ThreadPoolExecutor) -> Any:
    """
    Make the coroutine run, even if there is an event loop running (like by using nest_asyncio)

    Inspired by: https://github.com/jupyter/nbclient/pull/113
    """

    return pool.submit(asyncio.run, coroutine).result()
