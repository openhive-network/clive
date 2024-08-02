from __future__ import annotations

from typing import TYPE_CHECKING, Any

from clive.__private.ui.dashboard.dashboard_locked import DashboardLocked
from clive.__private.ui.dashboard.dashboard_unlocked import DashboardUnlocked
from clive.__private.ui.unlock.unlock import Unlock

from .checkers import assert_is_screen_active
from .textual_helpers import press_and_wait_for_screen, press_binding, write_text
from .utils import get_status, log_current_view

if TYPE_CHECKING:
    from textual.screen import Screen

    from .types import ClivePilot


async def unlock_body(pilot: ClivePilot, password: str, *, expected_screen: type[Screen[Any]] | None = None) -> None:
    """Do unlock when Unlock is current screen."""
    unlock_binding_desc = "Unlock wallet"
    assert_is_screen_active(pilot, Unlock)
    await write_text(pilot, password)
    if expected_screen:
        await press_and_wait_for_screen(pilot, "f2", expected_screen, key_description=unlock_binding_desc)
    else:
        await press_binding(pilot, "f2", unlock_binding_desc)
    log_current_view(pilot.app, nodes=True)
    assert get_status(pilot.app) == "unlocked", "Expected 'unlocked' status!"


async def unlock(pilot: ClivePilot, password: str) -> None:
    """Do unlock when DashboardLocked is current screen."""
    assert_is_screen_active(pilot, DashboardLocked)
    await press_and_wait_for_screen(pilot, "f5", Unlock)
    await unlock_body(pilot, password, expected_screen=DashboardUnlocked)
