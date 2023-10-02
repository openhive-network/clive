from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.currency_selector.currency_selector_base import (
    CurrencySelectorBase,
)
from clive.models import Asset

if TYPE_CHECKING:
    from clive.models.asset import AssetFactory


class CurrencySelector(CurrencySelectorBase[Asset.AnyT]):
    @staticmethod
    def _create_selectable() -> dict[str, AssetFactory[Asset.AnyT]]:
        return {
            "HBD": Asset.hbd,
            "HIVE": Asset.hive,
            "VESTS": Asset.vests,
        }
