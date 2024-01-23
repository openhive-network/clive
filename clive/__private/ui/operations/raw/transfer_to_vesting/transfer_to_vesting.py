from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.currency_selector.currency_selector_hive import CurrencySelectorHive
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.models import Asset
from schemas.operations import TransferToVestingOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class TransferToVesting(RawOperationBaseScreen):
    """Screen shows summary of `TransferToVesting` operation."""

    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self, account_name: str, hive_amount: str) -> None:
        """
        Initialize the TransferToVesting screen.

        Args:
        ----
        account_name: name of the transfer to vesting receiver.
        hive_amount: amount of hive in pretty format.
        """
        super().__init__()

        self._to_input = AccountNameInput(label="to", value=account_name, disabled=True)
        self._amount_input = NumericInput("amount", disabled=True)
        self._amount_input.input.value = hive_amount

        self._currency_selector = CurrencySelectorHive()
        self._currency_selector.disabled = True

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Transfer to vesting")
        yield Static("(also known as Power up)", id="power-up-name-info")
        with ScrollableContainer(), Body():
            yield InputLabel("from")
            yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
            yield PlaceTaker()
            yield from self._to_input.compose()
            yield PlaceTaker()
            yield from self._amount_input.compose()
            yield self._currency_selector

    def _create_operation(self) -> TransferToVestingOperation | None:
        amount = self._amount_input.value
        if not amount:
            return None

        return TransferToVestingOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=self._to_input.value,
            amount=Asset.hive(amount),
        )
