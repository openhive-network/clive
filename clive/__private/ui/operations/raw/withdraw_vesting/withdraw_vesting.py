from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

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


class Body(Grid):
    """All the content of the screen, excluding the title."""


class WithdrawVesting(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__account_input = AccountNameInput(placeholder=ACCOUNT_NAME2_PLACEHOLDER)
        self.__vesting_shares_input = NumericInput(label="vesting shares")

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Withdraw vesting")
        with ScrollableContainer(), Body():
            yield from self.__account_input.compose()
            yield from self.__vesting_shares_input.compose()

    def _create_operation(self) -> WithdrawVestingOperation | None:
        vesting_shares = self.__vesting_shares_input.value
        if not vesting_shares:
            return None

        return WithdrawVestingOperation(
            account=self.__account_input.value,
            vesting_shares=Asset.vests(vesting_shares),
        )
