from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.operations.operations import Operations

from .activate import activate_body
from .textual import is_key_binding_active
from .utils import log_current_view

if TYPE_CHECKING:
    from textual.pilot import Pilot


async def fast_broadcast(pilot: Pilot[int], activated: bool, password: str, view_info: bool = False) -> None:
    """Fast broadcast with optional activation if 'activated' == False."""
    if view_info:
        log_current_view(pilot.app)
    assert is_key_binding_active(pilot.app, "f5", "Fast broadcast"), "There are no expected binding for F5 key!"
    await pilot.press("f5")
    if not activated:
        await activate_body(pilot, password, view_info)
    assert isinstance(
        pilot.app.screen, Operations
    ), f"'fast_broadcast' expects 'Operations' to be the screen after finish! Current screen is: '{pilot.app.screen}'."
