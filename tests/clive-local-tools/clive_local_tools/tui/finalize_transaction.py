from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.screens.dashboard import DashboardUnlocked
from clive.__private.ui.screens.unlock import Unlock

from .textual_helpers import press_and_wait_for_screen
from .unlock import unlock_body

if TYPE_CHECKING:
    from .types import ClivePilot


async def finalize_transaction(pilot: ClivePilot, *, unlocked: bool = True, password: str | None = None) -> None:
    """Finalize transaction with optional unlock if 'unlocked' == False."""
    broadcast_binding_description = "Broadcast"
    if unlocked:
        await press_and_wait_for_screen(pilot, "f6", DashboardUnlocked, key_description=broadcast_binding_description)
    else:
        assert password is not None, "'password' cannot be None in case unlocked is False."
        await press_and_wait_for_screen(pilot, "f6", Unlock, key_description=broadcast_binding_description)
        await unlock_body(pilot, password, expected_screen=DashboardUnlocked)
