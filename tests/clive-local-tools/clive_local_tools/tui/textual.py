from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.pilot import Pilot


async def write_text(pilot: Pilot[int], text: str) -> None:
    """Useful for place text in any Input widget."""
    await pilot.press(*[c for c in text])  # noqa: C416
