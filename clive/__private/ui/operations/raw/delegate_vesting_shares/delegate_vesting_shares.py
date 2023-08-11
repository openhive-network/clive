from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import DelegateVestingSharesOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class DelegateVestingShares(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__delegatee_input = AccountNameInput(self, label="delegatee")
        self.__vesting_shares_input = AmountInput(self, label="vesting shares")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Delegate vesting shares")
            with ScrollableContainer(), Body():
                yield InputLabel("delegator")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="delegator-label")
                yield from self.__delegatee_input.compose()
                yield from self.__vesting_shares_input.compose()

    def _create_operation(self) -> DelegateVestingSharesOperation[Asset.Vests]:
        return DelegateVestingSharesOperation(
            delegator=self.app.world.profile_data.name,
            delegatee=self.__delegatee_input.value,
            vesting_shares=Asset.vests(self.__vesting_shares_input.value),
        )
