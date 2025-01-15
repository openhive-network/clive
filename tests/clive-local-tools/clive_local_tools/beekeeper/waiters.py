from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.waiters import wait_for

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


async def wait_for_beekeeper_to_close(beekeeper: Beekeeper, timeout: float = 1.0) -> None:
    async def is_not_running_locally() -> bool:
        return not await beekeeper.is_already_running_locally()

    await wait_for(is_not_running_locally, "Beekeeper was not closed", timeout=timeout)
