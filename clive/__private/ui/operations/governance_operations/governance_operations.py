from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.operations.governance_operations.governance_data import GovernanceDataProvider
from clive.__private.ui.operations.governance_operations.witness import Witnesses
from textual import on
from textual.containers import Container
from textual.widgets import Button, Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.operations.raw.account_witness_proxy.account_witness_proxy import AccountWitnessProxy
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class Proxy(ScrollableTabPane, CliveWidget):
    """TabPane with all content about proxy."""

    def __init__(self, title: TextType):
        super().__init__(title=title)
        self.__proxy_input = AccountNameInput()
        self.__proxy = self.app.world.profile_data.working_account.data.proxy

    def compose(self) -> ComposeResult:
        if not self.__proxy:
            yield Static("Current proxy: not set", classes="current-proxy-static")
            yield self.__proxy_input
            with Container(id="set-button-container"):
                yield CliveButton("Set proxy", id_="set-proxy-button")
            yield Static(
                "Notice: setting proxy will delete your witnesses votes and deactivate your proposal votes",
                id="proxy-set-information",
            )

    @on(Button.Pressed)
    def move_to_raw_screen(self) -> None:
        if not self.__proxy:
            self.app.push_screen(AccountWitnessProxy(is_raw=False, new_proxy=self.__proxy_input.value))


class Proposals(ScrollableTabPane):
    """TabPane with all content about proposals."""


class Governance(OperationBaseScreen):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def create_left_panel(self) -> ComposeResult:
        with GovernanceDataProvider(), CliveTabbedContent():
            yield Proxy("Proxy")
            yield Witnesses("Witnesses")
            yield Proposals("Proposals")
