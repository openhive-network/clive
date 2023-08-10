from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal

from clive.__private.ui.widgets.currency_selector.currency_selector_liquid import CurrencySelectorLiquid
from clive.__private.ui.widgets.inputs.amount_input import AmountInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models.asset import Asset


class AssetAmountInput(Horizontal):
    def __init__(self, label: str = "amount") -> None:
        self.__input_value = AmountInput(label=label)
        self.__currency_selector = CurrencySelectorLiquid()

        super().__init__()

    def compose(self) -> ComposeResult:
        label, input_ = self.__input_value.compose()
        currency_selector = self.__currency_selector

        class AssetInput(Horizontal):
            DEFAULT_CSS = """
                AssetInput Input {
                    width: 60%;
            }
            """

            def compose(self) -> ComposeResult:
                yield input_
                yield currency_selector

        yield label
        yield AssetInput()

    @property
    def amount(self) -> Asset.Hive | Asset.Hbd | None:
        if self.__input_value.value:
            return self.__currency_selector.create_asset(self.__input_value.value)
        return None
