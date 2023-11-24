from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
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
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self, is_raw: bool = True, new_proxy: str | None = None) -> None:
        super().__init__()
        self.__is_raw = is_raw
        self.__new_proxy = new_proxy

        self.__proxy_input = AccountNameInput(label="proxy")

    @property
    def proxy_to_be_set(self) -> str:
        if self.__is_raw:
            return self.__proxy_input.value

        if self.__new_proxy is None:
            return ""
        return self.__new_proxy

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Account witness proxy")
            with ScrollableContainer(), Body():
                yield InputLabel("account")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="account-label")
                if self.__is_raw:
                    yield from self.__proxy_input.compose()
                else:
                    yield from AccountNameInput(
                        label="new proxy",
                        value=self.__new_proxy if self.__new_proxy is not None else "Proxy will be removed",
                        disabled=True,
                    ).compose()

    def _create_operation(self) -> AccountWitnessProxyOperation:
        return AccountWitnessProxyOperation(account=self.app.world.profile_data.name, proxy=self.proxy_to_be_set)
