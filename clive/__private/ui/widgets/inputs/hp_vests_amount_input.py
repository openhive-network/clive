from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.models.asset import Asset
from clive.__private.ui.widgets.currency_selector.currency_selector_hp_vests import CurrencySelectorHpVests
from clive.__private.ui.widgets.inputs.asset_amount_base_input import AssetAmountInput

if TYPE_CHECKING:
    from clive.__private.ui.widgets.currency_selector.currency_selector_base import CurrencySelectorBase


class HPVestsAmountInput(AssetAmountInput[Asset.VotingT]):
    """An input for HP/VESTS amount."""

    def create_currency_selector(self) -> CurrencySelectorBase[Asset.VotingT]:
        return CurrencySelectorHpVests()
