from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.screens.operations import Operations
from clive.__private.ui.screens.transaction_summary import TransactionSummary
from clive_local_tools.tui.broadcast_transaction import broadcast_transaction
from clive_local_tools.tui.fast_broadcast import fast_broadcast
from clive_local_tools.tui.textual_helpers import press_and_wait_for_screen

if TYPE_CHECKING:
    from clive_local_tools.tui.types import ClivePilot, OperationProcessing


async def process_operation(
    pilot: ClivePilot,
    operation_processing: OperationProcessing,
    *,
    unlocked: bool = True,
    password: str | None = None,
) -> None:
    if operation_processing == "FAST_BROADCAST":
        await fast_broadcast(pilot, unlocked=unlocked, password=password)
    elif operation_processing == "ADD_TO_CART":
        await press_and_wait_for_screen(pilot, "f2", Operations)  # add to cart
        await press_and_wait_for_screen(pilot, "f2", TransactionSummary)
        await broadcast_transaction(pilot, unlocked=unlocked, password=password)
    else:
        await press_and_wait_for_screen(pilot, "f6", TransactionSummary)
        await broadcast_transaction(pilot, unlocked=unlocked, password=password)
