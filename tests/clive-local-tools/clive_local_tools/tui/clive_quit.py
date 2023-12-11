from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.pilot import Pilot


async def clive_quit(pilot: Pilot[int]) -> None:
    """Clean exit Clive from any screen."""
    await pilot.press("ctrl+x", "ctrl+x")
