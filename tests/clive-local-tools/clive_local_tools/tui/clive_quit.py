from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.quit.quit import Quit
from clive_local_tools.tui.textual import press_and_wait_for_screen, press_binding

if TYPE_CHECKING:
    from textual.pilot import Pilot


async def clive_quit(pilot: Pilot[int]) -> None:
    """Clean exit Clive from any screen."""
    quit_binding_desc = "Quit"
    await press_and_wait_for_screen(pilot, "ctrl+x", Quit, key_description=quit_binding_desc)
    await press_binding(pilot, "ctrl+x", quit_binding_desc)
