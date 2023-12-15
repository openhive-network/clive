from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.pilot import Pilot

    from .types import ASSET_TOKEN


async def choose_asset_token(pilot: Pilot[int], asset_token: ASSET_TOKEN) -> None:
    if asset_token == "HIVE":
        await pilot.press("down", "down", "enter")
