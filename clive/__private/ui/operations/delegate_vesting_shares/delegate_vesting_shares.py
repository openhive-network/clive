from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import DelegateVestingSharesOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from schemas.__private.hive_fields_basic_schemas import AssetVestsHF26


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class DelegateVestingShares(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__delegatee_input = Input(placeholder="e.g.: alice")
        self.__vesting_shares_input = Input(placeholder="e.g: 1.000")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Delegate vesting shares")
            with Body():
                yield Static("delegator", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="delegator-label")
                yield PlaceTaker()
                yield Static("delegatee", classes="label")
                yield self.__delegatee_input
                yield Static("vesting shares", classes="label")
                yield self.__vesting_shares_input

    def _create_operation(self) -> DelegateVestingSharesOperation[AssetVestsHF26]:
        return DelegateVestingSharesOperation(
            delegator=str(self.app.world.profile_data.name),
            delegatee=self.__delegatee_input.value,
            vesting_shares=Asset.vests(float(self.__vesting_shares_input.value)),
        )
