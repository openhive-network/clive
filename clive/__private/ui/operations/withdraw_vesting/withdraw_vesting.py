from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset, Operation
from schemas.operations import WithdrawVestingOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class WithdrawVesting(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__account_input = Input(placeholder="e.g.: hiveio")
        self.__vesting_shares_input = Input(placeholder="e.g.: 1.000")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Withdraw vesting")
            with Body():
                yield Static("account", classes="label")
                yield self.__account_input
                yield Static("vesting shares", classes="label")
                yield self.__vesting_shares_input

    def _create_operation(self) -> Operation | None:
        return WithdrawVestingOperation(
            account=self.__account_input.value,
            vesting_shares=Asset.vests(float(self.__vesting_shares_input.value)),
        )
