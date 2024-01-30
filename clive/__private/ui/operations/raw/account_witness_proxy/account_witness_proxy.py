from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from schemas.operations import AccountWitnessProxyOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class AccountWitnessProxy(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self, *, new_proxy: str | None) -> None:
        super().__init__()
        self._new_proxy = new_proxy

    @property
    def proxy_to_be_set(self) -> str:
        if self._new_proxy is None:
            return ""
        return self._new_proxy

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Account witness proxy")
        with ScrollableContainer(), Body():
            yield InputLabel("account")
            yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="account-label")
            yield from AccountNameInput(
                label="new proxy",
                value=self._new_proxy if self._new_proxy is not None else "Proxy will be removed",
                disabled=True,
            ).compose()

    def action_add_to_cart(self) -> None:
        super().action_add_to_cart()
        self.app.pop_screen()

    def _create_operation(self) -> AccountWitnessProxyOperation:
        return AccountWitnessProxyOperation(
            account=self.app.world.profile_data.working_account.name, proxy=self.proxy_to_be_set
        )
