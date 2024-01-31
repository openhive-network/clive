from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import ScrollableContainer, Vertical
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME2_PLACEHOLDER
from clive.models import Asset
from schemas.operations import WithdrawVestingOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Vertical):
    """All the content of the screen, excluding the title."""


class WithdrawVesting(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self, vests_value: Asset.Vests, calculation_factor: str | None = None) -> None:
        """
        Initialize the WithdrawVesting screen.

        Args:
        ----
        vests_value: Vests value to withdraw.
        calculation_factor: If HP has been converted to VESTS, pass the coefficient to inform the user of the calculation.
        """
        super().__init__()
        self._calculation_factor = calculation_factor

        self._account_input = AccountNameInput(
            placeholder=ACCOUNT_NAME2_PLACEHOLDER,
            value=self.app.world.profile_data.working_account.name,
            id_="withdraw-vesting-account-input",
        )

        vesting_shares_value = Asset.pretty_amount(vests_value)
        self._vesting_shares_input = NumericInput(label="vesting shares", id_="withdraw-vesting-shares-input")
        self._vesting_shares_input.input.value = vesting_shares_value

        self._account_input.disabled = True
        self._vesting_shares_input.disabled = True

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Withdraw vesting")
        with ScrollableContainer(), Body():
            yield self._account_input
            yield self._vesting_shares_input
            if self._calculation_factor is not None:
                yield Static(
                    (
                        "The given HP was converted to VESTS with a factor of: 1.000 HP ->"
                        f" {self._calculation_factor} VESTS"
                    ),
                    id="hp-vests-conversion-info",
                )

    def _create_operation(self) -> WithdrawVestingOperation | None:
        vesting_shares = self._vesting_shares_input.value
        if not vesting_shares:
            return None

        return WithdrawVestingOperation(
            account=self._account_input.value,
            vesting_shares=Asset.vests(vesting_shares),
        )
