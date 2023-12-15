from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.tui.fast_broadcast import fast_broadcast
from clive_local_tools.tui.finalize_transaction import finalize_transaction

if TYPE_CHECKING:
    from textual.pilot import Pilot

    from clive_local_tools.tui.types import OPERATION_PROCESSING


async def process_operation(
    pilot: Pilot[int], operation_processing: OPERATION_PROCESSING, activated: bool, password: str | None = None
) -> None:
    if operation_processing == "FAST_BROADCAST":
        await fast_broadcast(pilot, activated, password)
    else:  # "ADD_TO_CART" or "FINALIZE_TRANSACTION"
        if operation_processing == "ADD_TO_CART":
            await pilot.press("f2", "f2")  # add to cart, go to cart
        await finalize_transaction(pilot, activated, password)
