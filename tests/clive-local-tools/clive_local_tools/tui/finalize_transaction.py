from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.dashboard.dashboard import Dashboard
from clive.__private.ui.transaction_summary import TransactionSummaryFromCart

from .activate import activate_body
from .checkers import assert_is_dashboard
from .textual_helpers import press_and_wait_for_screen

if TYPE_CHECKING:
    from .types import ClivePilot


async def finalize_transaction(pilot: ClivePilot, *, activated: bool = True, password: str | None = None) -> None:
    """Finalize transaction with optional activation if 'activated' == False."""
    broadcast_binding_description = "Broadcast"

    await press_and_wait_for_screen(pilot, "f6", TransactionSummaryFromCart, wait_for_focused=False)
    if activated:
        await press_and_wait_for_screen(pilot, "f6", Dashboard, key_description=broadcast_binding_description)
    else:
        assert password is not None, "'password' cannot be None in case activated is False."
        await press_and_wait_for_screen(pilot, "f6", Activate, key_description=broadcast_binding_description)
        await activate_body(pilot, password)
    assert_is_dashboard(pilot, active=True)
