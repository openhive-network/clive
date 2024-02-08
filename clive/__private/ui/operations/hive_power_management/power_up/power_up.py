from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.bindings.operation_action_bindings import OperationActionBindings, _NotImplemented
from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_tab_pane import HPTabPane
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.currency_selector.currency_selector_hive import CurrencySelectorHive
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.models import Asset, Operation
from schemas.operations import TransferToVestingOperation as TransferToVesting

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class PlaceTaker(Static):
    """Static widget to ensure correct display of the grid."""


class ScrollablePart(ScrollableContainer):
    pass


class PowerUp(HPTabPane, OperationActionBindings):
    """TabPane with all content about power up."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType):
        super().__init__(title=title)
        self._receiver_input = AccountNameInput(label="receiver", value=self.working_account)
        self._asset_input = NumericInput()

        self._currency_selector = CurrencySelectorHive()
        self._currency_selector.disabled = True

    def create_tab_pane_content(self) -> ComposeResult:
        with ScrollablePart():
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
                yield CliveButton("All !", id_="clive-button-all")

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

    def _create_operation(self) -> Operation | None | _NotImplemented:
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
