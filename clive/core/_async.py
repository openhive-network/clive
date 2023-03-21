from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Coroutine


def asyncio_run(coroutine: Coroutine[Any, Any, Any]) -> Any:
    """
    Make the coroutine run, even if there is an event loop running (like by using nest_asyncio)

    Inspired by: https://github.com/jupyter/nbclient/pull/113
    """

    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coroutine).result()
