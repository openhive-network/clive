from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.transaction_summary import TransactionSummaryFromCart

from .activate import activate_body
from .textual import is_key_binding_active
from .utils import log_current_view

if TYPE_CHECKING:
    from textual.pilot import Pilot


async def finalize_transaction(pilot: Pilot[int], activated: bool, password: str, view_info: bool = False) -> None:
    """Finalize transaction with optional activation if 'activated' == False."""
    if view_info:
        log_current_view(pilot.app)
    assert is_key_binding_active(pilot.app, "f10", "Finalize transaction") or is_key_binding_active(
        pilot.app, "f10", "Summary"
    ), "There are no expected binding for F10 key!"
    await pilot.press("f10")
    assert isinstance(pilot.app.screen, TransactionSummaryFromCart), (
        "'finalize_transaction' expects 'TransactionSummaryFromCart' to be the final screen! "
        f"Current screen is: '{pilot.app.screen}'."
    )
    assert is_key_binding_active(pilot.app, "f10", "Broadcast"), "There are no expected binding for F10 key!"
    await pilot.press("f10")
    if not activated:
        await activate_body(pilot, password, view_info)
    assert isinstance(pilot.app.screen, DashboardActive), (
        "'finalize_transaction' expects 'DashboardActive' to be the screen after finish! "
        f"Current screen is: '{pilot.app.screen}'."
    )
