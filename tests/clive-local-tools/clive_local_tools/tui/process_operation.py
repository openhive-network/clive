from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.operations import Operations
from clive_local_tools.tui.fast_broadcast import fast_broadcast
from clive_local_tools.tui.finalize_transaction import finalize_transaction
from clive_local_tools.tui.textual_helpers import press_and_wait_for_screen

if TYPE_CHECKING:
    from clive_local_tools.tui.types import ClivePilot, OperationProcessing


async def process_operation(
    pilot: ClivePilot,
    operation_processing: OperationProcessing,
    activated: bool,
    password: str | None = None,
) -> None:
    if operation_processing == "FAST_BROADCAST":
        await fast_broadcast(pilot, activated, password)
    else:  # "ADD_TO_CART" or "FINALIZE_TRANSACTION"
        if operation_processing == "ADD_TO_CART":
            await press_and_wait_for_screen(pilot, "f2", Operations)  # add to cart
            await press_and_wait_for_screen(pilot, "f2", Cart)  # go to cart
        await finalize_transaction(pilot, activated, password)
