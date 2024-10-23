from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.screens.operations import Operations

from .textual_helpers import press_and_wait_for_screen

if TYPE_CHECKING:
    from .types import ClivePilot


async def fast_broadcast(pilot: ClivePilot) -> None:
    await press_and_wait_for_screen(pilot, "f5", Operations)
