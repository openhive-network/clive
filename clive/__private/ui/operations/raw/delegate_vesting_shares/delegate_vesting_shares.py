from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.placeholders_constants import ASSET_AMOUNT_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import DelegateVestingSharesOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class DelegateVestingShares(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__delegatee_input = AccountNameInput(label="delegatee")
        self.__vesting_shares_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Delegate vesting shares")
            with Body():
                yield Static("delegator", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="delegator-label")
                yield PlaceTaker()
                yield from self.__delegatee_input.compose()
                yield Static("vesting shares", classes="label")
                yield self.__vesting_shares_input

    def _create_operation(self) -> DelegateVestingSharesOperation[Asset.Vests]:
        return DelegateVestingSharesOperation(
            delegator=self.app.world.profile_data.name,
            delegatee=self.__delegatee_input.value,
            vesting_shares=Asset.vests(self.__vesting_shares_input.value),
        )
