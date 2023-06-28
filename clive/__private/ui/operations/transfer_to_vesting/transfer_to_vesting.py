from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset, Operation
from schemas.operations import TransferToVestingOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class TransferToVesting(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__to_input = Input(placeholder="e.g.: alice")
        self.__amount_input = Input(placeholder="e.g.: 5.000")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer to vesting")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("to", classes="label")
                yield self.__to_input
                yield Static("amount", classes="label")
                yield self.__amount_input

    def _create_operation(self) -> Operation | None:
        return TransferToVestingOperation(
            from_=str(self.app.world.profile_data.working_account.name),
            to=self.__to_input.value,
            amount=Asset.hive(float(self.__amount_input.value)),
        )
