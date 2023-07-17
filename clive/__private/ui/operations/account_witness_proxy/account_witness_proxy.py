from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import AccountWitnessProxyOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class AccountWitnessProxy(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__proxy_input = Input(placeholder="e.g.: hiveio")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Account witness proxy")
            with Body():
                yield Static("account", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="account-label")
                yield PlaceTaker()
                yield Static("proxy", classes="label")
                yield self.__proxy_input

    def _create_operation(self) -> AccountWitnessProxyOperation:
        return AccountWitnessProxyOperation(
            account=str(self.app.world.profile_data.name),
            proxy=self.__proxy_input.value,
        )
