from __future__ import annotations

from typing import TYPE_CHECKING, get_args

from clive.__private.ui.widgets.currency_selector.currency_selector_liquid import CurrencySelectorLiquid
from clive.models.asset import AssetFactoryHolder

from .types import ASSET_TOKEN

if TYPE_CHECKING:
    from textual.pilot import Pilot


async def choose_asset_token(pilot: Pilot[int], asset_token: str) -> None:
    assert asset_token in get_args(ASSET_TOKEN), f"Invalid asset_token: {asset_token}"
    assert isinstance(
        pilot.app.focused, CurrencySelectorLiquid
    ), f"'choose_asset_token' requires focus on 'CurrencySelectorLiquid'! Current focus set on: {pilot.app.focused}."
    if asset_token == "HIVE":
        await pilot.press("down", "down", "enter")
    selected_asset = pilot.app.query_one(CurrencySelectorLiquid).value
    assert (
        type(selected_asset) == AssetFactoryHolder
    ), f"Expected 'AssetFactoryHolder', current is {type(selected_asset)}."
    selected_asset_cls = selected_asset.asset_cls
    selected_asset_name = selected_asset_cls.get_asset_information().symbol[0]
    assert (
        selected_asset_name == asset_token
    ), f"Expected '{asset_token}' selection. Currently '{selected_asset_name}' is selected."
