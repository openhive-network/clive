from __future__ import annotations

from clive.__private.models.asset import Asset
from clive.__private.ui.widgets.currency_selector import CurrencySelectorHive
from clive.__private.ui.widgets.inputs.asset_amount_base_input import AssetAmountInput


class HiveAssetAmountInput(AssetAmountInput[Asset.Hive]):
    """An input for asset HIVE amount."""

    def create_currency_selector(self) -> CurrencySelectorHive:
        return CurrencySelectorHive()
