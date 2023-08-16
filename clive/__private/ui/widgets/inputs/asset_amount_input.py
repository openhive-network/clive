from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal

from clive.__private.ui.widgets.currency_selector.currency_selector_liquid import CurrencySelectorLiquid
from clive.__private.ui.widgets.inputs.amount_input import AmountInput

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget

    from clive.models.asset import Asset


class AssetAmountInput(Horizontal):
    DEFAULT_CSS = """
    AssetAmountInput {
        width: 0;
        height: 0;
    }
    """

    class Wrapper(Horizontal):
        DEFAULT_CSS = """
        Wrapper Input {
            width: 60%;
        }
        """

        def __init__(self, input_: AmountInput, currency_selector: CurrencySelectorLiquid) -> None:
            self.__input = input_
            self.__currency_selector = currency_selector
            super().__init__()

        def compose(self) -> ComposeResult:
            yield self.__input
            yield self.__currency_selector

    def __init__(self, to_mount: Widget, label: str = "amount") -> None:
        super().__init__()

        self.__input = AmountInput(self, label=label)
        self.__currency_selector = CurrencySelectorLiquid()

        to_mount.mount(self)

    def compose(self) -> ComposeResult:
        input_: AmountInput
        label, input_ = self.__input.compose()  # type: ignore[assignment]

        yield label
        yield self.Wrapper(input_, self.__currency_selector)

    @property
    def amount(self) -> Asset.Hive | Asset.Hbd | None:
        if self.__input.value:
            return self.__currency_selector.create_asset(self.__input.value)
        return None
