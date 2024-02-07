from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Static, TabPane

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_information_table import (
    HpInformationTable,
)
from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_vests_selector import (
    CurrencySelectorHpVests,
)
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class PlaceTaker(Static):
    pass


class DelegateHivePower(TabPane, CliveWidget):
    """TabPane with all content about delegate hp."""

    BINDINGS = [Binding("f2", "delegate", "Delegate")]
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType):
        """
        Initialize a TabPane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)
        self._account_input = AccountNameInput()
        self._asset_input = NumericInput()
        self._currency_selector = CurrencySelectorHpVests()

    def compose(self) -> ComposeResult:
        yield HpInformationTable()
        with Grid(id="delegate-inputs"):
            yield self._account_input
            yield PlaceTaker()
            yield self._asset_input
            yield self._currency_selector

    def action_delegate(self) -> None:
        pass
