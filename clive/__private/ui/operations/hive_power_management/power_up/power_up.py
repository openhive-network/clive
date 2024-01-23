from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static, TabPane

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.bindings.operation_action_bindings import OperationActionBindings
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.currency_selector.currency_selector_hive import CurrencySelectorHive
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.models import Asset
from schemas.operations import TransferToVestingOperation as TransferToVesting

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class PlaceTaker(Static):
    """Static widget to ensure correct display of the grid."""


class ScrollablePart(ScrollableContainer):
    pass


class PowerUp(TabPane, OperationActionBindings):
    """TabPane with all content about power up."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType):
        """
        Initialize a TabPane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)
        self._receiver_input = AccountNameInput(label="receiver", value=self.working_account)
        self._asset_input = NumericInput()

        self._currency_selector = CurrencySelectorHive()
        self._currency_selector.disabled = True

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield Static("Power up corresponds to a `transfer to vesting` operation", id="operation-name-info")
            yield Static(
                "Notice: `Power up` is different name for a `Transfer to vesting` operation",
                id="power-up-name-information",
            )
            with Grid(id="power-up-inputs"):
                yield self._receiver_input
                yield PlaceTaker()
                yield PlaceTaker()
                yield self._asset_input
                yield self._currency_selector
                yield CliveButton("All !", id_="clive-button-all", variant="success")

            yield Static(
                "Notice: Your governance voting power will be increased after 30 days", id="power-up-information"
            )  # TODO after merge new inputs - change to `Notice` widget

    @on(CliveButton.Pressed, "#clive-button-all")
    def fill_input_by_all(self) -> None:
        """If the balance is not 0, fill the amount input with the entire HIVE balance."""
        hive_balance = self.app.world.profile_data.working_account.data.hive_balance
        if float(hive_balance.amount) == 0:
            self.notify("Zero is not enough value to make power up", severity="warning")
            return
        self._asset_input.input.value = Asset.pretty_amount(hive_balance)

    def _create_operation(self) -> TransferToVesting | None:
        asset = self._asset_input.value
        if not asset:
            return None
        converted_asset = self._currency_selector.create_asset(asset)
        if converted_asset is None:
            return None

        receiver = self._receiver_input.value
        if not receiver:
            return None

        self._asset_input.input.value = ""
        return TransferToVesting(from_=self.working_account, to=receiver, amount=converted_asset)

    @property
    def working_account(self) -> str:
        return self.app.world.profile_data.working_account.name
