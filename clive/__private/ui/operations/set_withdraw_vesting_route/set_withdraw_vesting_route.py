from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import SetWithdrawVestingRouteOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class SetWithdrawVestingRoute(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        default_percent = str(get_default_from_model(SetWithdrawVestingRouteOperation, "percent"))
        default_auto_vest = str(get_default_from_model(SetWithdrawVestingRouteOperation, "auto_vest"))

        self.__to_account_input = Input(placeholder="e.g.: alice")
        self.__percent_input = Input(default_percent, placeholder="e.g.: 10")
        self.__auto_vest_input = Input(default_auto_vest, placeholder="e.g. True")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Set withdraw vesting route")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("to account", classes="label")
                yield self.__to_account_input
                yield Static("percent", classes="label")
                yield self.__percent_input
                yield Static("auto vest", classes="label")
                yield self.__auto_vest_input

    def _create_operation(self) -> SetWithdrawVestingRouteOperation:
        return SetWithdrawVestingRouteOperation(
            from_account=str(self.app.world.profile_data.name),
            to_account=self.__to_account_input.value,
            auto_vest=bool(self.__auto_vest_input.value),
            percent=int(self.__percent_input.value),
        )
