from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.screens.operations import Operations
from clive.__private.ui.screens.transaction_summary import TransactionSummary
from clive_local_tools.tui.broadcast_transaction import broadcast_transaction
from clive_local_tools.tui.textual_helpers import press_and_wait_for_screen, press_binding

if TYPE_CHECKING:
    from clive_local_tools.tui.types import ClivePilot, OperationProcessing


async def process_operation(pilot: ClivePilot, operation_processing: OperationProcessing) -> None:
    if operation_processing == "ADD_TO_CART":
        await press_binding(pilot, "f2", "Add to cart")
        await press_and_wait_for_screen(pilot, "escape", Operations)
        await press_and_wait_for_screen(pilot, "f2", TransactionSummary)
    else:
        await press_and_wait_for_screen(pilot, "f6", TransactionSummary)
    await broadcast_transaction(pilot)
