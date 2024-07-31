from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.operations.operations import Operations
from clive.__private.ui.unlock.unlock import Unlock

from .textual_helpers import press_and_wait_for_screen
from .unlock import unlock_body

if TYPE_CHECKING:
    from .types import ClivePilot


async def fast_broadcast(pilot: ClivePilot, *, unlocked: bool = True, password: str | None = None) -> None:
    """Fast broadcast with optional unlock if 'unlocked' == False."""
    if unlocked:
        await press_and_wait_for_screen(pilot, "f5", Operations)
    else:
        assert password is not None, "'password' cannot be None in case unlocked is False."
        await press_and_wait_for_screen(pilot, "f5", Unlock)
        await unlock_body(pilot, password, expected_screen=Operations)
