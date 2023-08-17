from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME2_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import WithdrawVestingOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class WithdrawVesting(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__account_input = AccountNameInput(placeholder=ACCOUNT_NAME2_PLACEHOLDER)
        self.__vesting_shares_input = AmountInput(label="vesting shares")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Withdraw vesting")
            with ScrollableContainer(), Body():
                yield from self.__account_input.compose()
                yield from self.__vesting_shares_input.compose()

    def _create_operation(self) -> WithdrawVestingOperation[Asset.Vests] | None:
        vesting_shares = self.__vesting_shares_input.value
        if not vesting_shares:
            return None

        return WithdrawVestingOperation(
            account=self.__account_input.value,
            vesting_shares=Asset.vests(vesting_shares),
        )
