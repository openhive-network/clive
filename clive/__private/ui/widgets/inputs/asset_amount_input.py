from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal

from clive.__private.ui.widgets.currency_selector.currency_selector_liquid import CurrencySelectorLiquid
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.__private.ui.widgets.placeholders_constants import NUMERIC_PLACEHOLDER
from clive.models.asset import Asset

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult
    from textual.widgets import Input


class AssetAmountInput(CustomInput[Asset.Hive | Asset.Hbd | None]):
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

        def __init__(self, input_: Input, currency_selector: CurrencySelectorLiquid) -> None:
            self.__input = input_
            self.__currency_selector = currency_selector
            super().__init__()

        def compose(self) -> ComposeResult:
            yield self.__input
            yield self.__currency_selector

    def __init__(
        self,
        label: str = "amount",
        *,
        placeholder: str = NUMERIC_PLACEHOLDER,
        tooltip: RenderableType | None = None,
        disabled: bool = False,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            label=label, placeholder=placeholder, tooltip=tooltip, disabled=disabled, id_=id_, classes=classes
        )

        self.__currency_selector = CurrencySelectorLiquid()

    def compose(self) -> ComposeResult:
        yield self._input_label
        yield self.Wrapper(self._input, self.__currency_selector)

    @property
    def value(self) -> Asset.Hive | Asset.Hbd | None:
        if self._input.value:
            return self.__currency_selector.create_asset(self._input.value)
        return None

    def _create_input(self) -> Input:
        custom_input = NumericInput(label=self._label, placeholder=self._placeholder, tooltip=self.tooltip)
        return custom_input._input
