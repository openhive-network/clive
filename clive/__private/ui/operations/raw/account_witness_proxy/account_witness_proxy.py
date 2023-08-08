from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME2_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import AccountWitnessProxyOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class AccountWitnessProxy(RawOperationBaseScreen):
    def __init__(self, delete_proxy: bool = False) -> None:
        self.__delete_proxy = delete_proxy
        super().__init__()

        self.__proxy_input = Input(placeholder=ACCOUNT_NAME2_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Account witness proxy")
            with Body():
                yield Static("account", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="account-label")
                if not self.__delete_proxy:
                    yield Static("proxy", classes="label")
                    yield self.__proxy_input
                else:
                    yield Static()
                    yield Static(
                        "Notice: after broadcast you will delete proxy for your account", id="proxy-notification"
                    )

    def _create_operation(self) -> AccountWitnessProxyOperation:
        return AccountWitnessProxyOperation(
            account=self.app.world.profile_data.name,
            proxy=self.__proxy_input.value,
        )
