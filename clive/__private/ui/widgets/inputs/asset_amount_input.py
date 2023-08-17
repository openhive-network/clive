from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal

from clive.__private.ui.widgets.currency_selector.currency_selector_liquid import CurrencySelectorLiquid
from clive.__private.ui.widgets.inputs.amount_input import AmountInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models.asset import Asset


class AssetAmountInput(Horizontal):
    """
    Class for selecting asset types and specifying their amounts.

    Examples:
    --------
    yield from instance_of_asset_amount_input.compose()

    Note:
    ----
    When using this widget, it will not be included in the list of nodes.
    Querying this widget is not supported.
    You must use it like the way in example.
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

    def __init__(self, label: str = "amount") -> None:
        self.__input = AmountInput(label=label)
        self.__currency_selector = CurrencySelectorLiquid()

        super().__init__()

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
