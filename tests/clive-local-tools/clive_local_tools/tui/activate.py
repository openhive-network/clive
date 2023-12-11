from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.dashboard.dashboard_inactive import DashboardInactive

from .textual import write_text
from .utils import get_mode, log_current_view

if TYPE_CHECKING:
    from textual.pilot import Pilot


async def activate_body(pilot: Pilot[int], password: str, view_info: bool = False) -> None:
    """Do activate when Activate is current screen."""
    assert isinstance(
        pilot.app.screen, Activate
    ), f"'activate_body' requires 'Activate' to be the current screen! Current screen is: '{pilot.app.screen}'."
    if view_info:
        log_current_view(pilot.app)
    await write_text(pilot, password)
    if view_info:
        log_current_view(pilot.app)
    await pilot.press("f2")
    if view_info:
        log_current_view(pilot.app, nodes=True)
    assert get_mode(pilot.app) == "active", "Expected 'active' mode!"


async def activate(pilot: Pilot[int], password: str, view_info: bool = False) -> None:
    """Do activate when DashboardInactive is current screen."""
    assert isinstance(
        pilot.app.screen, DashboardInactive
    ), f"'activate' requires 'DashboardInactive' to be the current screen! Current screen is: '{pilot.app.screen}'."
    await pilot.press("f4")
    await activate_body(pilot, password, view_info)
