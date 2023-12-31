from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.models import Asset
from schemas.operations import DelegateVestingSharesOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class DelegateVestingShares(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__delegatee_input = AccountNameInput(label="delegatee")
        self.__vesting_shares_input = NumericInput(label="vesting shares")

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Delegate vesting shares")
        with ScrollableContainer(), Body():
            yield InputLabel("delegator")
            yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="delegator-label")
            yield from self.__delegatee_input.compose()
            yield from self.__vesting_shares_input.compose()

    def _create_operation(self) -> DelegateVestingSharesOperation | None:
        vesting_shares = self.__vesting_shares_input.value
        if not vesting_shares:
            return None

        return DelegateVestingSharesOperation(
            delegator=self.app.world.profile_data.working_account.name,
            delegatee=self.__delegatee_input.value,
            vesting_shares=Asset.vests(vesting_shares),
        )
