from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.currency_selector.currency_selector_liquid import CurrencySelectorLiquid
from clive.models.asset import AssetFactoryHolder

from .checkers import assert_is_focused

if TYPE_CHECKING:
    from clive_local_tools.tui.types import ClivePilot

    from .types import LiquidAssetToken


async def choose_asset_token(pilot: ClivePilot, asset_token: LiquidAssetToken) -> None:
    assert_is_focused(pilot.app, CurrencySelectorLiquid)
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
