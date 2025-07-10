from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS
from clive.__private.ui.screens.quit import Quit
from clive_local_tools.tui.textual_helpers import press_and_wait_for_screen, press_binding

if TYPE_CHECKING:
    from clive_local_tools.tui.types import ClivePilot


async def clive_quit(pilot: ClivePilot) -> None:
    """Clean exit Clive from any screen."""
    quit_binding_desc = CLIVE_PREDEFINED_BINDINGS.app.quit.description
    await press_and_wait_for_screen(
        pilot, CLIVE_PREDEFINED_BINDINGS.app.quit.key, Quit, key_description=quit_binding_desc
    )
    await press_binding(pilot, CLIVE_PREDEFINED_BINDINGS.app.quit.key, quit_binding_desc)
