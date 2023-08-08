from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Input

from clive.__private.ui.widgets.currency_selector.currency_selector_liquid import CurrencySelectorLiquid
from clive.__private.ui.widgets.placeholders_constants import ASSET_AMOUNT_PLACEHOLDER

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models.asset import Asset


class AssetAmountInput(Horizontal):
    DEFAULT_CSS = """
    AmountInput CurrencySelectorLiquid {
        width: 1fr;
    }

    AmountInput Input {
        width: 2fr;
    }
    """

    def __init__(self) -> None:
        self.__input_value = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__currency_selector = CurrencySelectorLiquid()
        super().__init__()

    def compose(self) -> ComposeResult:
        yield self.__input_value
        yield self.__currency_selector

    @property
    def amount(self) -> Asset.Hive | Asset.Hbd | None:
        if self.__input_value.value:
            return self.__currency_selector.create_asset(self.__input_value.value)
        return None
