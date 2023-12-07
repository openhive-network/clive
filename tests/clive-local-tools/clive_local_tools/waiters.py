from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


async def wait_for_beekeeper_to_close_after_last_session_termination(
    beekeeper: Beekeeper, timeout: float = 1.0
) -> None:
    async def __wait_for_beekeeper_to_close() -> None:
        while beekeeper.is_already_running_locally():
            await asyncio.sleep(0.1)

    try:
        await asyncio.wait_for(__wait_for_beekeeper_to_close(), timeout=timeout)
    except asyncio.TimeoutError:
        raise AssertionError("Beekeeper was not closed after last session termination in the expected time.") from None
