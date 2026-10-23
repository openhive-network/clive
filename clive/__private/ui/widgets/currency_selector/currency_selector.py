from __future__ import annotations

from clive.__private.models.asset import (
    Asset,
    AssetFactoryHolder,
)
from clive.__private.ui.widgets.currency_selector.currency_selector_base import (
    CurrencySelectorBase,
)


class CurrencySelector(CurrencySelectorBase[Asset.AnyT]):
    @staticmethod
    def _create_selectable() -> dict[str, AssetFactoryHolder[Asset.AnyT]]:
        return {
            "HBD": AssetFactoryHolder(asset_kind=Asset.HBD_KIND, asset_factory=Asset.hbd),
            "HIVE": AssetFactoryHolder(asset_kind=Asset.HIVE_KIND, asset_factory=Asset.hive),
            "VESTS": AssetFactoryHolder(asset_kind=Asset.VESTS_KIND, asset_factory=Asset.vests),
        }
