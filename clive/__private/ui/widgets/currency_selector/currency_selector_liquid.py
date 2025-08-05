from __future__ import annotations

from clive.__private.models.asset import Asset, AssetFactoryHolder
from clive.__private.ui.widgets.currency_selector.currency_selector_base import (
    CurrencySelectorBase,
)


class CurrencySelectorLiquid(CurrencySelectorBase[Asset.LiquidT]):
    @staticmethod
    def _create_selectable() -> dict[str, AssetFactoryHolder[Asset.LiquidT]]:
        return {
            "HIVE": AssetFactoryHolder(asset_cls=Asset.Hive, asset_factory=Asset.hive),
            "HBD": AssetFactoryHolder(asset_cls=Asset.Hbd, asset_factory=Asset.hbd),
        }
