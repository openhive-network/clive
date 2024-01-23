from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Static, TabPane

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_information_table import (
    HpInformationTable,
)
from clive.__private.ui.operations.raw.transfer_to_vesting.transfer_to_vesting import TransferToVesting
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.currency_selector.currency_selector_hive import CurrencySelectorHive
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.models import Asset

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class PlaceTaker(Static):
    """Static widget to ensure correct display of the grid."""


class PowerUp(TabPane, CliveWidget):
    """TabPane with all content about power up."""

    BINDINGS = [Binding("f2", "power_up", "Power up")]

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType):
        """
        Initialize a TabPane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)
        working_account_name = self.app.world.profile_data.working_account.name
        self._account_name_input = AccountNameInput(label="receiver", value=working_account_name)
        self._asset_input = NumericInput()

        self._currency_selector = CurrencySelectorHive()
        self._currency_selector.disabled = True

    def compose(self) -> ComposeResult:
        yield HpInformationTable()
        with Grid(id="power-up-inputs"):
            yield self._account_name_input
            yield PlaceTaker()
            yield PlaceTaker()
            yield self._asset_input
            yield self._currency_selector
            yield CliveButton("All !", id_="clive-button-all")

        yield Static(
            "Notice ! Your governance voting power will be increased after 30 days", id="power-up-information"
        )  # TODO after merge new inputs - change to `Notice` widget

    @on(CliveButton.Pressed, "#clive-button-all")
    def fill_input_by_all(self) -> None:
        """If the balance is not 0, fill the amount input with the entire HIVE balance."""
        hive_balance = self.app.world.profile_data.working_account.data.hive_balance
        if float(hive_balance.amount) == 0:
            self.notify("Zero is not enough value to make power up", severity="warning")
            return
        self._asset_input.input.value = Asset.pretty_amount(hive_balance)

    def action_power_up(self) -> None:
        """If everything is OK with the input values - push the operation summary screen (TransferToVesting)."""
        asset = self._asset_input.value
        if not asset:
            return
        converted_asset = self._currency_selector.create_asset(asset)
        if converted_asset is None:
            return

        account_name = self._account_name_input.value

        if not account_name:
            return

        self._asset_input.input.value = ""
        self.app.push_screen(
            TransferToVesting(account_name=account_name, hive_amount=Asset.pretty_amount(converted_asset))
        )
