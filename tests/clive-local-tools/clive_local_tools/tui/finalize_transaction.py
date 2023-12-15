from __future__ import annotations

from typing import TYPE_CHECKING

from .activate import activate_body
from .utils import current_view, get_mode

if TYPE_CHECKING:
    from textual.pilot import Pilot


async def finalize_transaction(
    pilot: Pilot[int],
    activated: bool,
    password: str | None = None,
    view_info: bool = False,
) -> None:
    """Finalize transaction with optional activation if 'activated' == False."""
    if view_info:
        current_view(pilot.app)
    await pilot.press("f10", "f10")  # summary, finalize
    if not activated:
        assert password is not None, "For non-activated valid password expected!"
        await activate_body(pilot, password, view_info)
        assert get_mode(pilot.app) == "active", "Expected 'active' mode!"
