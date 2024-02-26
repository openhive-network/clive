from __future__ import annotations

from typing import TYPE_CHECKING

from .textual import key_press

if TYPE_CHECKING:
    from textual.pilot import Pilot


async def clive_quit(pilot: Pilot[int]) -> None:
    """Clean exit Clive from any screen."""
    await key_press(pilot, "ctrl+x", "ctrl+x")
