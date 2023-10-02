from __future__ import annotations

from clive.__private.ui.widgets.currency_selector.currency_selector_base import (
    CurrencySelectorBase,
)
from clive.models import Asset
from clive.models.asset import AssetFactoryHolder


class CurrencySelectorLiquid(CurrencySelectorBase[Asset.LiquidT]):
    @staticmethod
    def _create_selectable() -> dict[str, AssetFactoryHolder[Asset.LiquidT]]:
        return {
            "HBD": AssetFactoryHolder(asset_cls=Asset.Hbd, asset_factory=Asset.hbd),
            "HIVE": AssetFactoryHolder(asset_cls=Asset.Hive, asset_factory=Asset.hive),
        }
