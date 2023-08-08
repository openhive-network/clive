from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.amount_input import AmountInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import TransferToVestingOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class TransferToVesting(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__to_input = AccountNameInput(label="to")
        self.__amount_input = AmountInput()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer to vesting")
            with ScrollableContainer(), Body():
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield PlaceTaker()
                yield from self.__to_input.compose()
                yield from self.__amount_input.compose()

    def _create_operation(self) -> TransferToVestingOperation[Asset.Hive]:
        return TransferToVestingOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=self.__to_input.value,
            amount=Asset.hive(self.__amount_input.value),
        )
