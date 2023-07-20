from __future__ import annotations

from clive.__private.ui.widgets.currency_selector.currency_selector_base import (
    CurrencySelectorBase,
    CurrencySelectorCallableT,
)
from clive.models import Asset


class CurrencySelector(CurrencySelectorBase[Asset.AnyT]):
    @staticmethod
    def _create_selectable() -> dict[str, CurrencySelectorCallableT[Asset.AnyT]]:
        return {
            "HBD": Asset.hbd,
            "HIVE": Asset.hive,
            "VESTS": Asset.vests,
        }
