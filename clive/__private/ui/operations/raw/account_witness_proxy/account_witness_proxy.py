from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs_new.text_input import TextInput
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

    @property
    def working_account_name(self) -> str:
        return self.app.world.profile_data.working_account.name

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Account witness proxy")
        with ScrollableContainer(), Body():
            yield TextInput(
                "Account name",
                value=self.working_account_name,
                always_show_title=True,
                required=False,
                disabled=True,
            )
            yield TextInput(
                "New proxy",
                value=self._new_proxy if self._new_proxy is not None else "Proxy will be removed",
                always_show_title=True,
                required=False,
                disabled=True,
            )

    def action_add_to_cart(self) -> None:
        super().action_add_to_cart()
        self.app.pop_screen()

    def _create_operation(self) -> AccountWitnessProxyOperation:
        return AccountWitnessProxyOperation(account=self.working_account_name, proxy=self.proxy_to_be_set)
