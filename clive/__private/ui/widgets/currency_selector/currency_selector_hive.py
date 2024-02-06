from __future__ import annotations

from clive.__private.ui.widgets.currency_selector.currency_selector_base import CurrencySelectorBase
from clive.models import Asset
from clive.models.asset import AssetFactoryHolder


class CurrencySelectorHive(CurrencySelectorBase[Asset.Hive]):
    @staticmethod
    def _create_selectable() -> dict[str, AssetFactoryHolder[Asset.Hive]]:
        return {
            "HIVE": AssetFactoryHolder(asset_cls=Asset.Hive, asset_factory=Asset.hive),
        }
