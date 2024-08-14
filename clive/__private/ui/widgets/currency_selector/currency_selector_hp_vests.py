from __future__ import annotations

from clive.__private.models.asset import Asset, AssetFactoryHolder
from clive.__private.ui.widgets.currency_selector.currency_selector_base import CurrencySelectorBase


class CurrencySelectorHpVests(CurrencySelectorBase[Asset.Hive | Asset.Vests]):
    @staticmethod
    def _create_selectable() -> dict[str, AssetFactoryHolder[Asset.Hive | Asset.Vests]]:
        return {
            "HP": AssetFactoryHolder(asset_cls=Asset.Hive, asset_factory=Asset.hive),
            "VESTS": AssetFactoryHolder(asset_cls=Asset.Vests, asset_factory=Asset.vests),
        }
