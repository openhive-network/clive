from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import AccountWitnessProxyOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class AccountWitnessProxy(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__proxy_input = AccountNameInput(label="proxy")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Account witness proxy")
            with ScrollableContainer(), Body():
                yield InputLabel("account")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="account-label")
                yield PlaceTaker()
                yield from self.__proxy_input.compose()

    def _create_operation(self) -> AccountWitnessProxyOperation:
        return AccountWitnessProxyOperation(
            account=self.app.world.profile_data.name,
            proxy=self.__proxy_input.value,
        )
