from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.screens.dashboard import Dashboard

from .checkers import assert_is_dashboard
from .textual_helpers import press_and_wait_for_screen

if TYPE_CHECKING:
    from .types import ClivePilot


async def broadcast_transaction(pilot: ClivePilot) -> None:
    """Broadcast transaction with optional unlock if 'unlocked' == False."""
    broadcast_binding_description = "Broadcast"
    await press_and_wait_for_screen(pilot, "f6", Dashboard, key_description=broadcast_binding_description)
    assert_is_dashboard(pilot)
