from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.operations.operations import Operations

from .activate import activate_body
from .textual import press_and_wait_for_screen

if TYPE_CHECKING:
    from textual.pilot import Pilot


async def fast_broadcast(pilot: Pilot[int], activated: bool, password: str) -> None:
    """Fast broadcast with optional activation if 'activated' == False."""
    if activated:
        await press_and_wait_for_screen(pilot, "f5", Operations)
    else:
        await press_and_wait_for_screen(pilot, "f5", Activate)
        await activate_body(pilot, password, expected_screen=Operations)
