from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME2_PLACE_HOLDER, ASSET_AMOUNT_PLACEHOLDER
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

        self.__account_input = Input(placeholder=ACCOUNT_NAME2_PLACE_HOLDER)
        self.__vesting_shares_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Withdraw vesting")
            with Body():
                yield Static("account", classes="label")
                yield self.__account_input
                yield Static("vesting shares", classes="label")
                yield self.__vesting_shares_input

    def _create_operation(self) -> WithdrawVestingOperation[Asset.Vests]:
        return WithdrawVestingOperation(
            account=self.__account_input.value,
            vesting_shares=Asset.vests(self.__vesting_shares_input.value),
        )
