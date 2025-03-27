from __future__ import annotations

from clive.__private.models.asset import (
    AssetFactoryHolderHbd,
    AssetFactoryHolderHive,
    AssetFactoryHolderVests,
)
from clive.__private.ui.widgets.currency_selector.currency_selector_base import (
    CurrencySelectorBase,
)


class CurrencySelectorHive(CurrencySelectorBase):
    @staticmethod
    def _create_selectable() -> dict[str, AssetFactoryHolderHive | AssetFactoryHolderHbd | AssetFactoryHolderVests]:
        return {
            "HIVE": AssetFactoryHolderHive(),
        }

    def on_mount(self) -> None:
        self.disabled = True
