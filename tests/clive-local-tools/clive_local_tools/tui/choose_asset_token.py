from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.currency_selector.currency_selector_liquid import CurrencySelectorLiquid

if TYPE_CHECKING:
    from textual.pilot import Pilot

    from .types import ASSET_TOKEN


async def choose_asset_token(pilot: Pilot[int], asset_token: ASSET_TOKEN) -> None:
    assert isinstance(
        pilot.app.focused, CurrencySelectorLiquid
    ), f"'choose_asset_token' requires focus on 'CurrencySelectorLiquid'! Current focus set on: {pilot.app.focused}."
    if asset_token == "HIVE":
        await pilot.press("down", "down", "enter")
    assert (
        pilot.app.focused.query_one("SelectCurrent").label == asset_token  # type: ignore
    ), f"Expected '{asset_token}' selection. Currently '{pilot.app.focused.query_one('SelectCurrent').label}' selected."  # type: ignore
