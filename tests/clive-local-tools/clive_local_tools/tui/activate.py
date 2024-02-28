from __future__ import annotations

from typing import TYPE_CHECKING, Any

from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.dashboard.dashboard_inactive import DashboardInactive

from .checkers import assert_is_screen_active
from .textual import press_and_wait_for_screen, press_binding, write_text
from .utils import get_mode, log_current_view

if TYPE_CHECKING:
    from textual.screen import Screen

    from .types import ClivePilot


async def activate_body(pilot: ClivePilot, password: str, *, expected_screen: type[Screen[Any]] | None = None) -> None:
    """Do activate when Activate is current screen."""
    activate_binding_desc = "Ok"

    assert_is_screen_active(pilot, Activate)
    await write_text(pilot, password)
    if expected_screen:
        await press_and_wait_for_screen(pilot, "f2", expected_screen, key_description=activate_binding_desc)
    else:
        await press_binding(pilot, "f2", activate_binding_desc)
    log_current_view(pilot.app, nodes=True)
    assert get_mode(pilot.app) == "active", "Expected 'active' mode!"


async def activate(pilot: ClivePilot, password: str) -> None:
    """Do activate when DashboardInactive is current screen."""
    assert_is_screen_active(pilot, DashboardInactive)
    await press_and_wait_for_screen(pilot, "f4", Activate)
    await activate_body(pilot, password, expected_screen=DashboardActive)
