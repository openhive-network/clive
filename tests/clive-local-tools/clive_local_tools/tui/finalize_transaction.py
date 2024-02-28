from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.transaction_summary import TransactionSummaryFromCart

from .activate import activate_body
from .textual import press_and_wait_for_screen

if TYPE_CHECKING:
    from .types import ClivePilot


async def finalize_transaction(pilot: ClivePilot, activated: bool, password: str) -> None:
    """Finalize transaction with optional activation if 'activated' == False."""
    broadcast_binding_description = "Broadcast"

    await press_and_wait_for_screen(pilot, "f10", TransactionSummaryFromCart)
    if activated:
        await press_and_wait_for_screen(pilot, "f10", DashboardActive, key_description=broadcast_binding_description)
    else:
        await press_and_wait_for_screen(pilot, "f10", Activate, key_description=broadcast_binding_description)
        await activate_body(pilot, password, expected_screen=DashboardActive)
