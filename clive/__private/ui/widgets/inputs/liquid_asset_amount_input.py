from __future__ import annotations

from clive.__private.models.asset import Asset
from clive.__private.ui.widgets.currency_selector import CurrencySelectorLiquid
from clive.__private.ui.widgets.inputs.asset_amount_base_input import AssetAmountInput


class LiquidAssetAmountInput(AssetAmountInput[Asset.LiquidT]):
    def create_currency_selector(self) -> CurrencySelectorLiquid:
        return CurrencySelectorLiquid()
