from __future__ import annotations

from clive.__private.models import Asset
from clive.__private.models.asset import AssetFactoryHolder
from clive.__private.ui.widgets.currency_selector.currency_selector_base import (
    CurrencySelectorBase,
)


class CurrencySelectorHive(CurrencySelectorBase):
    @staticmethod
    def _create_selectable() -> dict[str, AssetFactoryHolder]:
        return {
            "HIVE": AssetFactoryHolder(asset_cls=Asset.Hive, asset_factory=Asset.hive),
        }

    def on_mount(self) -> None:
        self.disabled = True
